"""Hall-of-fame generator."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import io
from os import path

from . import storage
from .avatar import AvatarAdorner

class Glory:
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
        if not trending and not new_faces:  # We need to show SOMETHING!
            top_guns = self._assign_top()

        self._issue_badges(trending, new_faces, top_guns)

    def _assign_trending_and_new(self):
        contributors = self._count_commits()
        new_contributors = set(self.repo.new_contributors)

        trending = []
        new_faces = []

        # Up to 3 new faces, up to 5 trending.
        for username, num_commits in contributors:
            if username in new_contributors and len(new_faces) < 3:
                new_faces.append((username, num_commits))
            elif len(trending) < 5:
                trending.append((username, num_commits))
            else:
                break

        return trending, new_faces

    def _assign_top(self):
        top_guns = []
        for contributor in self.repo.top_contributors[:5]:
            top_guns.append((contributor.username, contributor.num_commits))
        top_guns.sort(key=lambda v: v[1], reverse=True)
        return top_guns

    def _issue_badges(self, trending, new_faces, top_guns):
        everyone = ([(u, n, 'trending') for u, n in trending] +
                    [(u, n, 'new') for u, n in new_faces] +
                    [(u, n, 'top') for u, n in top_guns])

        # Generate badges.
        profile_urls = []
        for i, entry in enumerate(everyone):
            username, num_commits, badge = entry

            adorner = AvatarAdorner()
            sourcerer_username, sourcerer_url = self._map_to_sourcerer(username) 
            if sourcerer_url:
                adorner.init_with_sourcerer(sourcerer_url)
                profile_urls.append(
                    'https://sourcerer.io/' + sourcerer_username)
            else:
                adorner.init_with_face(self.repo.avatars[username])
                profile_urls.append('https://github.com/' + username)
            adorner.adorn(badge, num_commits)

            image_path = path.join(self._get_image_dir(), '%d.svg' % i)
            storage.save_file(image_path, adorner.get_avatar_svg())

        # Save the profile link file.
        storage.save_file(self._get_link_file_path(), '\n'.join(profile_urls))

        # Generate a test HTML.
        f = io.StringIO()
        for i in range(len(profile_urls)):
            h = '<a href="%s"><img height="68px" src="images/%d.svg"></a>\n'
            f.write(h % (profile_urls[i], i))
        test_html_path = self._get_test_html_path()
        storage.save_file(test_html_path, f.getvalue())
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

    def _cleanup(self):
        image_dir = self._get_image_dir()
        storage.remove_subtree(image_dir)
        storage.make_dirs(image_dir)

        link_file = self._get_link_file_path()
        storage.remove_file(link_file)

    def _get_link_file_path(self):
        return path.join(self._get_repo_dir(), 'links.txt')

    def _get_test_html_path(self):
        return path.join(self._get_repo_dir(), 'test.html')

    def _get_image_dir(self):
        return path.join(self._get_repo_dir(), 'images')

    def _get_repo_dir(self):
        return path.join(self.repo.user, self.repo.owner, self.repo.name)
