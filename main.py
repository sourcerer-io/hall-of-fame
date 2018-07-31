"""Google Cloud Functions for Hall of Fame."""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import os

import flask
from google.cloud import pubsub

import fame.storage
from fame.github_tracker import RepoTracker, TrackerError
from fame.glory import Glory


class CloudError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Manage:
    """Management commands."""
    ADD = 'add'          # Add a repo to tracking.
    REMOVE = 'remove'    # Remove a repo from tracking.
    LIST = 'list'        # List repos for a given user.

    @staticmethod
    def is_valid(command):
        return command in [Manage.ADD, Manage.REMOVE, Manage.LIST]


class Refresh:
    """Refresh commands."""
    REFRESH = 'refresh'  # Update repo stats and remake badges (update+glorify).
    REFRESH_ALL = 'refresh-all'  # Refresh all repos.

    @staticmethod
    def is_valid(command):
        return command in [Refresh.REFRESH, Refresh.REFRESH_ALL]


def error(message):
    raise CloudError(message)


def error_if_false(expression, message):
    if not expression:
        error(message)


def update_and_glorify(tracker, glory):
    tracker.update()
    repo = tracker.load()
    glory.make(repo)


def make_error_response(error_code, message):
    response = flask.jsonify({'status': 'error', 'message': message})
    response.status_code = error_code
    return response


def fame_manage(request):
    """HTTP Google cloud function. Adds/Removes/Lists repos."""
    try:
        data = request.get_json()
        error_if_false(data, 'No payload')

        command = data.get('command', None)
        error_if_false(Manage.is_valid(command), 'Invalid command %s' % command)

        user = data.get('user', None)
        error_if_false(user, 'User is required')

        if command in [Manage.ADD, Manage.REMOVE]:
            owner = data.get('owner', None)
            error_if_false(owner, 'Repo owner is required')

            repo = data.get('repo', None)
            error_if_false(repo, 'Repo is required')

        bucket = os.environ.get('bucket', None)
        error_if_false(bucket, 'Google cloud bucket is required')
        fame.storage.configure_for_google_cloud(os.environ['bucket'])

        tracker = RepoTracker()
        result = {'status': 'ok'}

        if command == Manage.ADD:
            tracker.configure(user, owner, repo)
            tracker.add()
        elif command == Manage.REMOVE:
            tracker.configure(user, owner, repo)
            tracker.remove()
        elif command == Manage.LIST:
            directory = []
            for _, owner, repo in RepoTracker.list(user):
                directory.append({'user': user, 'owner': owner, 'repo': repo})
            result['data'] = directory

        return flask.jsonify(result)

    except Exception as e:
        print('e %s' % str(e))
        return make_error_response(400, str(e))


def fame_refresh(data, context):
    """Google cloud function. Adds refresh tasks for repos to pubsub."""
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
