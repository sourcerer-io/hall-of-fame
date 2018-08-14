"""GitHub repo tracker tracks commits in the last 7 days."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import json
import re

from collections import namedtuple
from datetime import datetime, timedelta
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


ListRepoResult = namedtuple(
    'RepoListResult',
    ['user', 'owner', 'repo', 'status', 'last_modified', 'error_message'])


class RepoTracker:
    KNOWN_BOTS = ['pyup-bot']

    def configure(self, user, owner, repo,
                  sourcerer_api_origin=None,
                  sourcerer_api_secret=None,
                  github_token=None):
        """Sets tracker to a repo.

        If you supply API origin, you will also need API secret. API is used
        if provided, and if github token was not directly supplied. In case,
        there is neither API nor token supplied, anonymous access to GitHub
        is used.

        Args:
          user: GitHub user who set up tracking for this repo.
          owner: GitHub repo owner.
          repo: GitHub repo, repo URL is github.com/:owner/:repo.
          sourcerer_api_origin: API origin, used to fetch GitHub token.
          sourcerer_api_secret: Secret for API authentication.
          github_token: GitHub token supplied directly.
        """
        self.user = user
        self.owner = owner
        self.repo = repo
        self.github_token = github_token
        if not github_token and sourcerer_api_origin:
            if not sourcerer_api_secret:
                raise TrackerError('Sourcerer API secret required')

            self.github_token = self._load_github_token(
                sourcerer_api_origin, sourcerer_api_secret)

    def error(self, message):
        raise TrackerError('%s %s' % (message, self._repo_str()))

    def add(self):
        """Adds a repo to track.

        """
        repo_dir = self._get_repo_dir()
        storage.make_dirs(repo_dir)
        repo = pb.Repo(owner=self.owner, name=self.repo, user=self.user)

        repo_path = self._get_repo_path()
        if storage.file_exists(repo_path):
            self.error('Repo exists')
        self._save(repo)
        print('i Added repo %s' % (self._repo_str()))

    def remove(self):
        """Removes GitHub repo from tracking."""
        if not storage.file_exists(self._get_repo_path()):
            self.error('Repo not found')

        repo_dir = self._get_repo_dir()
        storage.remove_subtree(repo_dir)

        owner_dir = self._get_owner_dir()
        if not storage.list_dir(owner_dir):
            storage.remove_subtree(owner_dir)

        user_dir = self._get_user_dir()
        if not storage.list_dir(user_dir):
            storage.remove_subtree(user_dir)
        print('i Removed repo %s' % (self._repo_str()))

    @staticmethod
    def list(user=None):
        """Returns all tracked GitHub repos."""
        if user:
            if not storage.dir_exists(user):
                return
            users = [user]
        else:
            users = storage.list_dir('', include_files=False)

        for user in users:
            for owner in storage.list_dir(user):
                owner_dir = path.join(user, owner)
                for repo_name in storage.list_dir(owner_dir):
                    repo_path = path.join(owner_dir, repo_name, 'repo')
                    repo = RepoTracker._load_repo(repo_path)
                    if not repo:
                        continue
                    last_modified = storage.last_modified(repo_path)
                    yield ListRepoResult(user, owner, repo_name,
                                         repo.status, last_modified,
                                         repo.error_message)

    def load(self):
        repo = RepoTracker._load_repo(self._get_repo_path())
        if not repo:
            self.error('Repo not found')

        return repo

    def update(self):
        repo = self.load()
        try:
            avatars = dict(repo.avatars)
            self._update_latest_commits(repo, avatars)
            self._update_top_contributors(repo, avatars)
            self._update_new_contributors(repo)

            repo.ClearField('avatars')
            for username, avatar in avatars.items():
                repo.avatars[username] = avatar

            repo.status = pb.Repo.SUCCESS
            repo.ClearField('error_message')

            self._save(repo)
            print('i Updated repo %s' % self._repo_str())

        except Exception as e:
            repo.status = pb.Repo.ERROR
            repo.error_message = str(e)
            self._save(repo)
            print('e Error updating repo %s: %s' % (self._repo_str(), str(e)))

    @staticmethod
    def _load_repo(repo_path):
        if not storage.file_exists(repo_path):
            return None

        repo = pb.Repo()
        text_format.Merge(storage.load_file(repo_path), repo)

        return repo

    def _repo_str(self):
        return '%s:%s/%s' % (self.user, self.owner, self.repo)

    def _load_github_token(self, sourcerer_api_origin, sourcerer_api_secret):
        try:
            PATH = 'api/face/hof/token'
            args = 'username=%s&provider=github' % self.user
            url = '%s/%s?%s' % (sourcerer_api_origin, PATH, args)
            headers = {'Authorization': sourcerer_api_secret}
            request = Request(url, None, headers=headers)
            response = urlopen(request)
            data = self._get_json(response)
            return data['token']
        except HTTPError as e:
            print('e Failed to fetch GitHub API token: %s' % e.reason)
            raise

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
        last_known = (repo.recent_commits[0].sha if repo.recent_commits
                      else None)
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

            if author in RepoTracker.KNOWN_BOTS:
                print('i Skipping bot commit %s by %s' % (sha, author))
                continue

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

        url = self._make_github_url(repo.owner, repo.name, 'contributors')
        r = self._open_github_url(url)
        contributors = self._get_json(r)

        for contrib in contributors[:20]:
            username = contrib['login']
            if username in RepoTracker.KNOWN_BOTS:
                print('i Skipping bot in top contributors: %s' % username)
                continue

            committer = repo.top_contributors.add()
            committer.username = username
            committer.num_commits = contrib['contributions']
            avatars[username] = contrib['avatar_url']

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
            if e.code == 403:
                print('e %s. GitHub API rate limit?' % e.reason)
            raise

    def _get_json(self, response):
        data = response.read().decode()
        return json.loads(data)
