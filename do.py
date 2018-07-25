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

from fame.github_tracker import RepoTracker, TrackerError
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
    parser.add_argument('--work_dir', type=str, required=True,
                        help='Working directory to store data')
    parser.add_argument('--token', type=str, help='Github API token')
    args = parser.parse_args()

    if is_repo_command(args.command):
        if not args.user:
            parser.error('Must provide repo user')
        if not args.owner:
            parser.error('Must provide repo owner')
        if not args.repo:
            parser.error('Must provide repo name')

    if not os.path.isdir(args.work_dir):
        parser.error('--work_dir must be an existing directory')

    return args


def main():
    args = parse_args()

    tracker = RepoTracker(args.work_dir)
    if is_repo_command(args.command):
        tracker.configure(args.user, args.owner, args.repo, args.token)

    try:
        if args.command == 'add':
            tracker.add()
        elif args.command == 'remove':
            tracker.remove()
        elif args.command == 'update':
            tracker.update()
        elif args.command == 'list':
            for user, owner, repo in tracker.list():
                print('%s:%s/%s' % (user, owner, repo))
        elif args.command == 'print':
            repo = tracker.load()
            print(repo)
        elif args.command == 'glorify':
            repo = tracker.load()
            glory = Glory(args.work_dir)
            glory.make(repo)
    except TrackerError as e:
        print('e %s' % str(e))


if __name__ == '__main__':
    main()
