"""GitHub repo tracker tracks commits in the last 7 days."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import json
import re

from datetime import datetime, timedelta, timezone
from os import path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import dateparser
from google.protobuf import text_format

from . import storage
from . import repo_pb2 as pb


class TrackerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RepoTracker:
    def configure(self, user, owner, repo, github_token=None):
        """Sets tracker to a repo.

        Args:
          user: GitHub user who set up tracking for this repo.
          owner: GitHub repo owner.
          repo: GitHub repo, repo URL is github.com/:owner/:repo.
        """
        self.user = user
        self.owner = owner
        self.repo = repo
        self.github_token = github_token

    def error(self, message):
        raise TrackerError(
            '%s %s:%s/%s' % (message, self.user, self.owner, self.repo))

    def add(self):
        """Adds a repo to track.

        """
        repo_dir = self._get_repo_dir()
        storage.make_dirs(repo_dir)
        repo = pb.Repo(owner=self.owner, name=self.repo, user=self.user)

        repo_path = self._get_repo_path()
        if storage.path_exists(repo_path):
            self.error('Repo exists')
        self._save(repo)
        print('i Added repo %s:%s/%s' % (self.user, self.owner, self.repo))

    def remove(self):
        """Removes GitHub repo from tracking."""
        if not storage.path_exists(self._get_repo_path()):
            self.error('Repo not found')

        repo_dir = self._get_repo_dir()
        storage.remove_subtree(repo_dir)

        owner_dir = self._get_owner_dir()
        if not storage.list_dir(owner_dir):
            storage.remove_subtree(owner_dir)

        user_dir = self._get_user_dir()
        if not storage.list_dir(user_dir):
            storage.remove_subtree(user_dir)
        print('i Removed repo %s:%s/%s' % (self.user, self.owner, self.repo))

    @staticmethod
    def list(user=None):
        """Returns all tracked GitHub repos."""
        if user:
            if not storage.path_exists(user):
                return
            users = [user]
        else:
            users = storage.list_dir('', include_files=False)

        for user in users:
            for owner in storage.list_dir(user):
                owner_dir = path.join(user, owner)
                for repo in storage.list_dir(owner_dir):
                    yield user, owner, repo

    def load(self):
        repo_path = self._get_repo_path()
        if not storage.path_exists(repo_path):
            self.error('Repo not found')

        repo = pb.Repo()
        text_format.Merge(storage.load_file(repo_path), repo)

        return repo

    def update(self):
        repo = self.load()
        avatars = dict(repo.avatars)
        self._update_latest_commits(repo, avatars)
        self._update_top_contributors(repo, avatars)
        self._update_new_contributors(repo)

        repo.ClearField('avatars')
        for username, avatar in avatars.items():
            repo.avatars[username] = avatar

        self._save(repo)
        print('i Updated repo %s:%s/%s' % (self.user, self.owner, self.repo))

    def _get_repo_path(self):
        return path.join(self._get_repo_dir(), 'repo')

    def _get_repo_dir(self):
        return path.join(self._get_owner_dir(), self.repo)

    def _get_owner_dir(self):
        return path.join(self._get_user_dir(), self.owner)

    def _get_user_dir(self):
        return self.user

    def _save(self, repo):
        repo_path = self._get_repo_path()
        storage.save_file(repo_path, text_format.MessageToString(repo))

    def _update_latest_commits(self, repo, avatars):
        """Makes sure repo contains 7 days worth of most recent commits."""
        last_known = repo.recent_commits[0].sha if repo.recent_commits else None
        commits = []
        now = datetime.utcnow()
        since = now - timedelta(days=7)
        for c in self._get_github_commits(repo.owner, repo.name, since=since):
            if 'sha' not in c:
                print('w GitHub commit without hash. Weird. Skipping')
                continue
            sha = c['sha']
            if sha == last_known:
                break

            try:
                # Chop 'Z' out of the timestamp.
                commit_date = c['commit']['author']['date'][:-1]
                author = c['author']['login']
                avatars[author] = c['author']['avatar_url']
            except:
                print('w Author, date, or avatar missing. Skipping %s' % sha)

            commit = pb.Commit(sha=sha, timestamp=commit_date, username=author)
            commits.append(commit)

        # We need to keep just last week's worth of commits.
        commits.extend(repo.recent_commits)
        while commits and dateparser.parse(commits[-1].timestamp) < since:
            commits.pop()

        repo.ClearField('recent_commits')
        repo.recent_commits.extend(commits)

        # Remove unnecessary avatars.
        valid_users = {c.username for c in repo.recent_commits}
        for username in list(avatars.keys()):
            if username not in valid_users:
                del avatars[username]

    def _update_top_contributors(self, repo, avatars):
        repo.ClearField('top_contributors')
        if repo.recent_commits:
            return

        url = self._make_github_url(repo.owner, repo.name, 'contributors')
        r = self._open_github_url(url)
        contributors = self._get_json(r)

        for contrib in contributors[:5]:  # We just want top 5.
            committer = repo.top_contributors.add()
            committer.username = contrib['login']
            committer.num_commits = contrib['contributions']
            avatars[committer.username] = contrib['avatar_url']

    def _update_new_contributors(self, repo):
        repo.ClearField('new_contributors')
        if not repo.recent_commits:
            return

        now = datetime.utcnow()
        until = now - timedelta(days=7)
        everyone = {c.username for c in repo.recent_commits}
        new_contributors = set()
        for username in everyone:
            commit = next(self._get_github_commits(repo.owner, repo.name,
                                                   author=username,
                                                   until=until), None)
            if not commit:
                new_contributors.add(username)

        repo.new_contributors.extend(list(new_contributors))

    def _get_github_commits(self, owner, repo,
                            author=None, since=None, until=None):
        url = self._make_github_url(owner, repo, 'commits')
        args = ['per_page=100']
        if author:
            args.append('author=' + author)
        if since:
            args.append('since=' + self._format_date(since))
        if until:
            args.append('until=' + self._format_date(until))
        if args:
            url += '?' + '&'.join(args)

        last_url = None
        while url:
            r = self._open_github_url(url)
            if url != last_url:
                url, last_url = self._get_next_last_url(r.headers)
            else:
                url = None
            data = self._get_json(r)
            for commit in data:
                yield commit

    def _format_date(self, date):
        return date.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _get_next_last_url(self, headers):
        if 'Link' not in headers:
            return None, None

        link = headers['Link']
        matches = re.findall(r'<([^>]+)>; rel="(next|last)"', link)
        rels = {rel: link_url for link_url, rel in matches}
        return rels.get('next', None), rels.get('last', None)

    def _make_github_url(self, owner, repo, what):
        return 'https://api.github.com/repos/%s/%s/%s' % (owner, repo, what)

    def _open_github_url(self, url):
        try:
            headers = {}
            if self.github_token:
                headers['Authorization'] = 'token %s' % self.github_token
            request = Request(url, None, headers=headers)
            return urlopen(request)
        except HTTPError as e:
            print('e %s. API limit?' % e.reason)
            raise

    def _get_json(self, request):
        data = request.read().decode()
        return json.loads(data)
