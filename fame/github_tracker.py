"""GitHub repo tracker tracks commits in the last 7 days."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import os
from datetime import datetime, timedelta, timezone
from os import path

import dateparser
from google.protobuf import text_format
from github import Github

from . import github_repo_pb2 as proto


class TrackerError(Exception):
    def __init__(self, message):
        super().__init__(message)


class RepoTracker:
    def __init__(self, work_dir):
        self.work_dir = work_dir

    def configure(self, user, owner, repo):
        """Sets tracker to a repo.

        Args:
          user: GitHub user who set up tracking for this repo.
          owner: GitHub repo owner.
          repo: GitHub repo, repo URL is github.com/:owner/:repo.
        """
        self.user = user
        self.owner = owner
        self.repo = repo

    def error(self, message):
        raise TrackerError(
            '%s %s:%s/%s' % (message, self.user, self.owner, self.repo))

    def add(self):
        """Adds a repo to track.

        """
        owner_dir = path.join(self.work_dir, self.user, self.owner)
        os.makedirs(owner_dir, exist_ok=True)
        repo = proto.Repo(
            owner=self.owner, name=self.repo, user=self.user)

        repo_path = path.join(owner_dir, self.repo)
        if path.exists(repo_path):
            self.error('Repo exists')
        with open(path.join(owner_dir, self.repo), 'w') as f:
            f.write(text_format.MessageToString(repo))
        print('i Added repo %s:%s/%s' % (self.user, self.owner, self.repo))

    def remove(self):
        """Removes GitHub repo from tracking."""
        user_dir = path.join(self.work_dir, self.user)
        owner_dir = path.join(user_dir, self.owner)
        repo_path = path.join(owner_dir, self.repo)
        if path.isfile(repo_path):
            os.remove(repo_path)
        else:
            self.error('Repo not found')
        if not os.listdir(owner_dir):
            os.rmdir(owner_dir)
        if not os.listdir(user_dir):
            os.rmdir(user_dir)
        print('i Removed repo %s:%s/%s' % (self.user, self.owner, self.repo))

    def list(self):
        """Returns all tracked GitHub repos."""
        for user in os.listdir(self.work_dir):
            user_dir = path.join(self.work_dir, user)
            for owner in os.listdir(user_dir):
                owner_dir = path.join(user_dir, owner)
                for repo in os.listdir(owner_dir):
                    yield user, owner, repo

    def load(self):
        repo_path = path.join(self.work_dir, self.user, self.owner, self.repo)
        if not path.exists(repo_path):
            self.error('Repo not found')
        with open(repo_path) as f:
            repo = proto.Repo()
            text_format.Merge(f.read(), repo)

        return repo

    def save(self, repo):
        repo_path = path.join(self.work_dir, self.user, self.owner, self.repo)
        with open(repo_path, 'w') as f:
            f.write(text_format.MessageToString(repo))


    def update(self):
        repo = self.load()
        last_known = repo.recent_commits[0].sha if repo.recent_commits else None

        github = Github()  # TODO(sergey): Provide user's token here.
        gh_repo = github.get_repo('%s/%s' % (self.owner, self.repo)) 

        # Get latest commits.
        commits = []
        now = datetime.utcnow()
        since = now - timedelta(days=7)
        for c in gh_repo.get_commits(since=since):
            if c.sha == last_known:
                break

            commit = proto.Commit(sha=c.sha,
                                  timestamp=c.commit.author.date.isoformat(),
                                  username=c.author.login,
                                  avatar_url=c.author.avatar_url)
            commits.append(commit)

        # We need to keep just last week's worth of commits.
        commits.extend(repo.recent_commits)
        while dateparser.parse(commits[-1].timestamp) < since:
            commits.pop()

        repo.ClearField('recent_commits')
        repo.recent_commits.extend(commits)

        self.save(repo)
