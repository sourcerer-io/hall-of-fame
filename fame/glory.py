"""Hall-of-fame generator."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import json
import io
from os import path
from urllib.request import urlopen

from . import storage
from .avatar import AvatarAdorner, Spacer


class Glory:
    MAX_NEW = 3       # Max number of new faces.
    MAX_TRENDING = 4  # Max number of trending contributors.
    MAX_ALL = 7       # Max number of entries.

    LEGEND_URL = 'https://github.com/sourcerer-io/hall-of-fame'

    def __init__(self, sourcerer_origin, sourcerer_api_origin=None):
        """Creates an instance of Glory.

        Args:
          sourcerer_origin: Origin for Sourcerer URLs, e.g. avatars.
          sourcerer_api_origin: Origin for Sourcerer API.
        """
        self.sourcerer_origin = sourcerer_origin
        self.sourcerer_api_origin = sourcerer_api_origin
        if not self.sourcerer_api_origin:
            self.sourcerer_api_origin = self.sourcerer_origin
        self.user_mapping = {}

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
        self._install()
        print('i Glorified %s:%s/%s' % (repo.user, repo.owner, repo.name))

    def _assign_trending_and_new(self):
        contribs = self._count_commits()
        new_contribs = set(self.repo.new_contributors)

        trending = []
        new_faces = []

        for username, num_commits in contribs:
            if username in new_contribs and len(new_faces) < Glory.MAX_NEW:
                new_faces.append((username, num_commits))
            else:
                trending.append((username, num_commits))

        # If we have more trending that we have spots for, let's see if we can
        # drop top contributors from the trending list. The motivation here is
        # top contributors always contribute, so they probably don't require
        # much motivation :)
        if len(trending) > Glory.MAX_TRENDING:
            top3 = [c.username for c in self.repo.top_contributors][:3]
            top_trending = [u for u, _ in trending if u in top3]
            to_drop = top_trending[:Glory.MAX_TRENDING - len(trending)]
            trending = [(u, c) for u, c in trending if u not in to_drop]

        trending = trending[:Glory.MAX_TRENDING]

        return trending, new_faces

    def _assign_top(self, excluded_users):
        top_guns = []
        max_top_guns = Glory.MAX_ALL - len(excluded_users)
        for contrib in self.repo.top_contributors:
            if not max_top_guns:
                break
            if contrib.username not in excluded_users:
                top_guns.append((contrib.username, contrib.num_commits))
                max_top_guns -= 1
        top_guns.sort(key=lambda v: v[1], reverse=True)
        return top_guns

    def _issue_badges(self, trending, new_faces, top_guns):
        everyone = ([(u, n, 'new') for u, n in new_faces] +
                    [(u, n, 'trending') for u, n in trending] +
                    [(u, n, 'top') for u, n in top_guns])
        self._map_users_to_sourcerer([u for u, _, _, in everyone])

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
        link_path = self._get_link_file_path(temp=True)
        storage.save_file(link_path, '\n'.join(profile_urls) + '\n')

        # Generate a test HTML.
        f = io.StringIO()
        for i in range(len(profile_urls)):
            h = '<a href="%s"><img src="images/%d.svg"></a>'
            f.write(h % (profile_urls[i], i))
        test_html_path = self._get_test_html_path(temp=True)
        storage.save_file(test_html_path, f.getvalue(), 'text/html')

    def _count_commits(self):
        contributors = {}
        for commit in self.repo.recent_commits:
            username = commit.username
            contributors[username] = contributors.get(username, 0) + 1
        contributors = list(contributors.items())
        contributors.sort(key=lambda v: v[1], reverse=True)

        return contributors

    def _map_users_to_sourcerer(self, github_usernames):
        url = self._get_sourcerer_mapping_url(github_usernames)
        data = urlopen(url).read().decode()
        parsed = json.loads(data)
        self.user_mapping = {k: v for k, v in parsed.items() if v}

    def _map_to_sourcerer(self, github_username):
        if github_username not in self.user_mapping:
            return None, None

        sourcerer_username = self.user_mapping[github_username]
        url = self._get_sourcerer_avatar_url(sourcerer_username)
        return self.user_mapping[github_username], url

    def _get_sourcerer_mapping_url(self, github_usernames):
        return '%s/api/face/hof/match?names=%s' % (
            self.sourcerer_api_origin, ','.join(github_usernames))

    def _get_sourcerer_avatar_url(self, sourcerer_username):
        return '%s/assets/avatar/%s' % (self.sourcerer_origin, sourcerer_username)

    def _save_svg(self, num, svg):
        image_path = self._get_image_file_path(num, temp=True)
        storage.save_file(image_path, svg, 'image/svg+xml')

    def _cleanup(self):
        temp_dir = self._get_base_dir(temp=True)
        storage.remove_subtree(temp_dir)
        storage.make_dirs(temp_dir)

        temp_image_dir = self._get_image_dir(temp=True)
        storage.make_dirs(temp_image_dir)

        image_dir = self._get_image_dir(temp=False)
        storage.make_dirs(image_dir)

    def _install(self):
        # Never delete anything from base dir so that serving never fails.
        # Since we always make the same number of entries, we simply overwrite.
        temp_image_dir = self._get_image_dir(temp=True)
        image_dir = self._get_image_dir(temp=False)

        for filename in storage.list_dir(temp_image_dir):
            storage.move_file(path.join(temp_image_dir, filename),
                              path.join(image_dir, filename))

        temp_link_file = self._get_link_file_path(temp=True)
        link_file = self._get_link_file_path(temp=False)
        storage.move_file(temp_link_file, link_file)

        temp_html_file = self._get_test_html_path(temp=True)
        html_file = self._get_test_html_path(temp=False)
        storage.move_file(temp_html_file, html_file)

        storage.remove_subtree(self._get_base_dir(temp=True))

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
