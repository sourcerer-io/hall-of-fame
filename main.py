"""Google Cloud Functions for Hall of Fame."""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import os

import fame.storage
from fame.github_tracker import RepoTracker, TrackerError
from fame.glory import Glory


class CloudError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Command:
    ADD = 'add'         # Add a repo to tracking.
    REMOVE = 'remove'   # Remove a repo from tracking.
    UPDATE = 'refresh'  # Update repo stats and refresh badges (update+glorify).

    @staticmethod
    def is_valid(command):
        return command in [Command.ADD, Command.REMOVE, Command.UPDATE]


def error(message):
    raise CloudError(message)


def error_if_false(expression, message):
    if not expression:
        error(message)


def glorify(data, context):
    """Google cloud function."""
    try:
        attrs = data['attributes']
        command = attrs.get('command', None)
        error_if_false(Command.is_valid(command), 'Invalid command')

        user = attrs.get('user', None)
        error_if_false(user, 'User is required')

        owner = attrs.get('owner', None)
        error_if_false(owner, 'Repo owner is required')

        repo = attrs.get('repo', None)
        error_if_false(repo, 'Repo is required')

        bucket = os.environ.get('bucket', None)
        error_if_false(bucket, 'Google cloud bucket is required')
        fame.storage.configure_for_google_cloud(os.environ['bucket'])

        tracker = RepoTracker()
        tracker.configure(user, owner, repo)

        if command == Command.ADD:
            tracker.add()
        elif command == Command.REMOVE:
            tracker.remove()
        elif command == Command.UPDATE:
            tracker.update()
            repo = tracker.load()
            glory = Glory()
            glory.make(repo)

    except Exception as e:
        print('e %s' % str(e))
