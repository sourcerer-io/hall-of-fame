"""CLI for hall of fame.

Commands
    add: Adds a repo to track.
    remove: Deletes a tracked repo.
    list: Lists all tracked repos.
    update: Updates a repo.
    print: Prints a tracked repo.
    glorify: Generate the hall of fame.
"""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import argparse
import os.path

import fame.storage
from fame.github_tracker import RepoTracker
from fame.glory import Glory


def is_repo_command(command):
    return command in ['add', 'remove', 'update', 'print', 'glorify']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str,
                        choices=['add', 'remove', 'list',
                                 'update', 'print', 'glorify'],
                        help='Command to execute')
    parser.add_argument('--user', type=str,
                        help='Github user that tracks a repo')
    parser.add_argument('--owner', type=str,
                        help='Github user that owns a repo')
    parser.add_argument('--repo', type=str,
                        help='Github repo name, excluding owner')
    parser.add_argument('--work_dir', type=str,
                        help='Working directory to store data')
    parser.add_argument('--gcloud_bucket', type=str,
                        help='Google cloud bucket to store data')
    parser.add_argument('--token', type=str, help='Github API token')
    parser.add_argument('--sourcerer_origin', type=str,
                        default='https://sourcerer.io',
                        help='Sourcerer origin')
    parser.add_argument('--sourcerer_api_origin', type=str,
                        help='Sourcerer API origin')
    parser.add_argument('--sourcerer_api_secret', type=str,
                        help='Sourcerer API secret')
    args = parser.parse_args()

    if is_repo_command(args.command):
        if not args.user:
            parser.error('Must provide repo user')
        if not args.owner:
            parser.error('Must provide repo owner')
        if not args.repo:
            parser.error('Must provide repo name')
        if not args.sourcerer_origin:
            parser.error('Must provide Sourcerer origin')

    if args.work_dir and not os.path.isdir(args.work_dir):
        parser.error('--work_dir must be an existing directory')

    if not args.work_dir and not args.gcloud_bucket:
        parser.error('Either --work_dir or --gcloud_bucket must be provided')

    return args


def main():
    args = parse_args()

    if args.work_dir:
        fame.storage.configure_for_local(args.work_dir)
    elif args.gcloud_bucket:
        fame.storage.configure_for_google_cloud(args.gcloud_bucket)

    try:
        tracker = RepoTracker()
        if is_repo_command(args.command):
            tracker.configure(args.user, args.owner, args.repo,
                              args.sourcerer_api_origin,
                              args.sourcerer_api_secret,
                              args.token)

        if args.command == 'add':
            tracker.add()
        elif args.command == 'remove':
            tracker.remove()
        elif args.command == 'update':
            tracker.update()
        elif args.command == 'list':
            for user, owner, repo in RepoTracker.list(args.user):
                print('%s:%s/%s' % (user, owner, repo))
        elif args.command == 'print':
            repo = tracker.load()
            print(repo)
        elif args.command == 'glorify':
            repo = tracker.load()
            glory = Glory(args.sourcerer_origin, args.sourcerer_api_origin)
            glory.make(repo)
    except Exception as e:
        print('e %s' % str(e))


if __name__ == '__main__':
    main()
