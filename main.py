"""Google Cloud Functions for Hall of Fame."""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import os
from google.cloud import pubsub

import fame.storage
from fame.github_tracker import RepoTracker, TrackerError
from fame.glory import Glory


class CloudError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Command:
    ADD = 'add'          # Add a repo to tracking.
    REMOVE = 'remove'    # Remove a repo from tracking.
    REFRESH = 'refresh'  # Update repo stats and remake badges (update+glorify).

    @staticmethod
    def is_valid(command):
        return command in [Command.ADD, Command.REMOVE, Command.REFRESH]


def error(message):
    raise CloudError(message)


def error_if_false(expression, message):
    if not expression:
        error(message)


def update_and_glorify(tracker, glory):
    tracker.update()
    repo = tracker.load()
    glory.make(repo)


def fame_glorify(data, context):
    """Google cloud function. Adds/Removes/Refreshes a repo."""
    try:
        attrs = data['attributes']
        command = attrs.get('command', None)
        error_if_false(Command.is_valid(command),
                       'Invalid command %s' % command)

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
        glory = Glory()

        if command == Command.ADD:
            tracker.add()
            update_and_glorify(tracker, glory)
        elif command == Command.REMOVE:
            tracker.remove()
        elif command == Command.REFRESH:
            update_and_glorify(tracker, glory)

    except Exception as e:
        print('e %s' % str(e))


def fame_enqueue_refresh(data, context):
    """Google cloud function. Adds refresh tasks for all repos to pubsub."""
    try:
        project = os.environ.get('project', None)
        error_if_false(project, 'Google pubsub project is required')

        topic = os.environ.get('topic', None)
        error_if_false(topic, 'Google pubsub topic is required')

        bucket = os.environ.get('bucket', None)
        error_if_false(bucket, 'Google cloud bucket is required')
        fame.storage.configure_for_google_cloud(os.environ['bucket'])

        client = pubsub.PublisherClient()
        full_topic = 'projects/%s/topics/%s' % (project, topic)

        tracker = RepoTracker()
        for user, owner, repo in tracker.list():
           client.publish(full_topic, b'', command=Command.REFRESH,
                          user=user, owner=owner, repo=repo)
           print('i Enqueued for refresh %s:%s/%s' % (user, owner, repo))

    except Exception as e:
        print('e %s' % str(e))
