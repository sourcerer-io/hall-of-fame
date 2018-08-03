"""Hall-of-fame generator."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import io
from os import path

from . import storage
from .avatar import AvatarAdorner, Spacer


class Glory:
    MAX_NEW = 3       # Max number of new faces.
    MAX_TRENDING = 4  # Max number of trending contributors.
    MAX_ALL = 7       # Max number of entries.

    LEGEND_URL = 'https://github.com/sourcerer-io/hall-of-fame'

    def __init__(self):
        # Load Sourcerer / GitHub mapping. This is temporary.
        # TODO(sergey): Replace with a call to Sourcerer API.
        data = storage.load_file('users.csv')
        lines = data.strip().split('\n')
        self.users = {}
        for line in lines:
            github_user, sourcerer_user = line.strip().split(',')
            self.users[github_user] = sourcerer_user

    def make(self, repo):
        """Makes hall of fame for a repo, a protobuf."""
        self.repo = repo
        self._cleanup()

        trending, new_faces = self._assign_trending_and_new()

        top_guns = []
        if len(trending) + len(new_faces) < Glory.MAX_ALL:
            excluded_users = set([v[0] for v in trending + new_faces])
            top_guns = self._assign_top(excluded_users)

        self._issue_badges(trending, new_faces, top_guns)
        print('i Glorified %s:%s/%s' % (repo.user, repo.owner, repo.name))

    def _assign_trending_and_new(self):
        contribs = self._count_commits()
        new_contribs = set(self.repo.new_contributors)

        trending = []
        new_faces = []

        for username, num_commits in contribs:
            if username in new_contribs and len(new_faces) < Glory.MAX_NEW:
                new_faces.append((username, num_commits))
            elif len(trending) < Glory.MAX_TRENDING:
                trending.append((username, num_commits))
            else:
                break

        return trending, new_faces

    def _assign_top(self, excluded_users):
        top_guns = []
        max_top_guns = Glory.MAX_ALL - len(excluded_users)
        for contrib in self.repo.top_contributors[:max_top_guns]:
            if contrib.username not in excluded_users:
                top_guns.append((contrib.username, contrib.num_commits))
        top_guns.sort(key=lambda v: v[1], reverse=True)
        return top_guns

    def _issue_badges(self, trending, new_faces, top_guns):
        everyone = ([(u, n, 'new') for u, n in new_faces] +
                    [(u, n, 'trending') for u, n in trending] +
                    [(u, n, 'top') for u, n in top_guns])

        # Generate badges.
        profile_urls = []
        for i, entry in enumerate(everyone):
            username, num_commits, badge = entry

            adorner = AvatarAdorner()
            sourcerer_user, sourcerer_url = self._map_to_sourcerer(username)
            if sourcerer_url:
                adorner.init_with_sourcerer(sourcerer_url)
                profile_urls.append(
                    'https://sourcerer.io/' + sourcerer_user)
            else:
                adorner.init_with_face(self.repo.avatars[username])
                profile_urls.append('https://github.com/' + username)

            adorner.adorn(badge, num_commits)
            self._save_svg(i, adorner.get_avatar_svg())

        # Make a legend image and a link.
        spacer = Spacer()
        spacer.make_legend()
        self._save_svg(len(everyone), spacer.get_spacer_svg())
        profile_urls.append(Glory.LEGEND_URL)

        # Fill up the remaining slots with empty SVGs.
        spacer.make_empty()
        for i in range(len(everyone) + 1, Glory.MAX_ALL + 1):  # +1 for legend.
            self._save_svg(i, spacer.get_spacer_svg())
            profile_urls.append(Glory.LEGEND_URL)

        # Save the profile link file.
        link_path = self._get_link_file_path()
        storage.save_file(link_path, '\n'.join(profile_urls) + '\n')

        # Generate a test HTML.
        f = io.StringIO()
        for i in range(len(profile_urls)):
            h = '<a href="%s"><img height="68px" src="images/%d.svg"></a>\n'
            f.write(h % (profile_urls[i], i))
        test_html_path = self._get_test_html_path()
        storage.save_file(test_html_path, f.getvalue(), 'text/html')
        print('i Saved test HTML to %s' % test_html_path)

    def _count_commits(self):
        contributors = {}
        for commit in self.repo.recent_commits:
            username = commit.username
            contributors[username] = contributors.get(username, 0) + 1
        contributors = list(contributors.items())
        contributors.sort(key=lambda v: v[1], reverse=True)

        return contributors

    def _map_to_sourcerer(self, github_username):
        # TODO(sergey): Replace with a call to backend.
        if github_username not in self.users:
            return None, None

        url = 'https://sourcerer.io/avatar/' + self.users[github_username]
        return self.users[github_username], url

    def _save_svg(self, num, svg, temp=False):
        image_path = self._get_image_file_path(num, temp)
        storage.save_file(image_path, svg, 'image/svg+xml')

    def _cleanup(self):
        image_dir = self._get_image_dir()
        storage.remove_subtree(image_dir)
        storage.make_dirs(image_dir)

        link_file = self._get_link_file_path()
        storage.remove_file(link_file)

        test_file = self._get_test_html_path()
        storage.remove_file(test_file)

    def _get_link_file_path(self, temp=False):
        return path.join(self._get_base_dir(temp), 'links.txt')

    def _get_test_html_path(self, temp=False):
        return path.join(self._get_base_dir(temp), 'test.html')

    def _get_image_file_path(self, num, temp=False):
        return path.join(self._get_image_dir(temp), '%d.svg' % num)

    def _get_image_dir(self, temp=False):
        return path.join(self._get_base_dir(temp), 'images')

    def _get_base_dir(self, temp):
        repo_dir = path.join(self.repo.user, self.repo.owner, self.repo.name)
        return path.join(repo_dir, 'temp') if temp else repo_dir
