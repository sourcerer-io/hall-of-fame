"""Google Cloud Functions for Hall of Fame."""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import os

import flask
from google.cloud import pubsub

import fame.ssl_hack
import fame.storage
from fame.github_tracker import RepoTracker
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
    REFRESH = 'refresh'  # Update repo stats and make badges (update+glorify).
    REFRESH_ALL = 'refresh-all'  # Refresh all repos.

    @staticmethod
    def is_valid(command):
        return command in [Refresh.REFRESH, Refresh.REFRESH_ALL]


def error(message):
    raise CloudError(message)


def error_if_false(expression, message):
    if not expression:
        error(message)


def make_error_response(error_code, message):
    response = flask.jsonify({'status': 'error', 'message': message})
    response.status_code = error_code
    return response


def configure_storage():
    bucket = os.environ.get('bucket', None)
    error_if_false(bucket, 'Google cloud bucket is required')
    fame.storage.configure_for_google_cloud(os.environ['bucket'])


def get_fame_pubsub_topic():
    project = os.environ.get('project', None)
    error_if_false(project, 'Google pubsub project is required')

    topic = os.environ.get('topic', None)
    error_if_false(topic, 'Google pubsub topic is required')

    return 'projects/%s/topics/%s' % (project, topic)


def fame_manage(request):
    """HTTP Google cloud function. Adds/Removes/Lists repos."""
    try:
        data = request.get_json()
        error_if_false(data, 'No payload')

        command = data.get('command', None)
        error_if_false(Manage.is_valid(command),
                       'Invalid command %s' % command)

        user = data.get('user', None)
        error_if_false(user, 'User is required')

        configure_storage()
        topic = get_fame_pubsub_topic()  # Let it fail early.

        if command in [Manage.ADD, Manage.REMOVE]:
            owner = data.get('owner', None)
            error_if_false(owner, 'Repo owner is required')

            repo = data.get('repo', None)
            error_if_false(repo, 'Repo is required')

        tracker = RepoTracker()
        result = {'status': 'ok'}

        if command == Manage.ADD:
            tracker.configure(user, owner, repo)
            tracker.add()
            client = pubsub.PublisherClient()
            client.publish(topic, b'', command=Refresh.REFRESH,
                           user=user, owner=owner, repo=repo)
        elif command == Manage.REMOVE:
            tracker.configure(user, owner, repo)
            tracker.remove()
        elif command == Manage.LIST:
            directory = []
            for item in RepoTracker.list(user):
                modified = item.last_modified.strftime('%Y-%m-%dT%H:%M:%SZ')
                directory.append({
                    'user': item.user,
                    'owner': item.owner,
                    'repo': item.repo,
                    'status': item.status,
                    'last_modified': modified,
                    'message': item.error_message})
            result['data'] = directory

        return flask.jsonify(result)

    except Exception as e:
        print('e %s' % str(e))
        return make_error_response(400, str(e))


def fame_refresh(data, context):
    """Pubsub Google cloud function. Refreshes repos."""
    try:
        attrs = data['attributes']
        command = attrs.get('command', None)
        error_if_false(Refresh.is_valid(command),
                       'Invalid command %s' % command)

        sourcerer_origin = os.environ.get('sourcerer_origin', None)
        error_if_false(sourcerer_origin, 'Sourcerer origin is required')
        sourcerer_api_origin = os.environ.get('sourcerer_api_origin', None)
        sourcerer_api_secret = os.environ.get('sourcerer_api_secret', None)
        if os.environ.get('no_ssl_host_check', None) == '1':
            fame.ssl_hack.disable_ssl_host_check()

        configure_storage()
        topic = get_fame_pubsub_topic()  # Let it fail early.

        if command == Refresh.REFRESH_ALL:  # Enqueue refresh for all repos.
            client = pubsub.PublisherClient()
            for user, owner, repo, _, _, _ in RepoTracker.list():
                client.publish(topic, b'', command=Refresh.REFRESH,
                               user=user, owner=owner, repo=repo)
                print('i Enqueued for refresh %s:%s/%s' % (user, owner, repo))

        elif command == Refresh.REFRESH:  # Do an actual refresh for a repo.
            user = attrs.get('user', None)
            error_if_false(user, 'User is required')

            owner = attrs.get('owner', None)
            error_if_false(owner, 'Repo owner is required')

            repo = attrs.get('repo', None)
            error_if_false(repo, 'Repo is required')

            tracker = RepoTracker()
            tracker.configure(user, owner, repo,
                              sourcerer_api_origin=sourcerer_api_origin,
                              sourcerer_api_secret=sourcerer_api_secret)
            tracker.update()

            glory = Glory(sourcerer_origin, sourcerer_api_origin)
            glory.make(tracker.load())

    except Exception as e:
        print('e %s' % str(e))
