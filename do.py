"""CLI for hall of fame.

Commands
    add: Adds a repo to track.
    remove: Deletes a tracked repo.
    list: Lists all tracked repos.
    update: Updates a repo.
    print: Prints a tracked repo.
    glorify: Generate the hall of fame.
    code: Generate MD or RST integration code.
"""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import argparse
import os.path

from tabulate import tabulate

import fame.storage
import fame.ssl_hack
from fame.code_gen import make_md_code, make_rst_code
from fame.github_tracker import RepoTracker
from fame.glory import Glory


class Command:
    ADD = 'add'
    REMOVE = 'remove'
    UPDATE = 'update'
    LIST = 'list'
    PRINT = 'print'
    GLORIFY = 'glorify'
    CODE = 'code'

    @staticmethod
    def is_repo_command(command):
        return command in [
            Command.ADD, Command.REMOVE, Command.UPDATE,
            Command.PRINT, Command.GLORIFY]

    @staticmethod
    def get_all():
        return [
            Command.ADD, Command.REMOVE, Command.UPDATE,
            Command.LIST, Command.PRINT, Command.GLORIFY, Command.CODE]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str,
                        choices=Command.get_all(),
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
    parser.add_argument('--format', type=str, choices=['md', 'rst'],
                        default='md', help='Code format to generate')
    parser.add_argument('--token', type=str, help='Github API token')
    parser.add_argument('--sourcerer_origin', type=str,
                        default='https://sourcerer.io',
                        help='Sourcerer origin')
    parser.add_argument('--sourcerer_api_origin', type=str,
                        help='Sourcerer API origin')
    parser.add_argument('--sourcerer_api_secret', type=str,
                        help='Sourcerer API secret')
    parser.add_argument('--no_ssl_host_check', action='store_true',
                        default=False,
                        help='Disable SSL host checks, useful for debugging')
    args = parser.parse_args()

    if Command.is_repo_command(args.command) or args.command == Command.CODE:
        if not args.user:
            parser.error('Must provide repo user')
        if not args.owner:
            parser.error('Must provide repo owner')
        if not args.repo:
            parser.error('Must provide repo name')

    if Command.is_repo_command(args.command) and not args.sourcerer_origin:
        parser.error('Must provide Sourcerer origin')

    if args.work_dir and not os.path.isdir(args.work_dir):
        parser.error('--work_dir must be an existing directory')

    if not args.work_dir and not args.gcloud_bucket:
        parser.error('Either --work_dir or --gcloud_bucket must be provided')

    return args


def main():
    args = parse_args()

    if args.no_ssl_host_check:
        fame.ssl_hack.disable_ssl_host_check()

    if args.work_dir:
        fame.storage.configure_for_local(args.work_dir)
    elif args.gcloud_bucket:
        fame.storage.configure_for_google_cloud(args.gcloud_bucket)

    try:
        tracker = RepoTracker()
        if Command.is_repo_command(args.command):
            tracker.configure(args.user, args.owner, args.repo,
                              args.sourcerer_api_origin,
                              args.sourcerer_api_secret,
                              args.token)

        if args.command == Command.ADD:
            tracker.add()
        elif args.command == Command.REMOVE:
            tracker.remove()
        elif args.command == Command.UPDATE:
            tracker.update()
        elif args.command == Command.LIST:
            table = []
            for result in RepoTracker.list(args.user):
                user, owner, repo, status, modified, error = result
                modified = modified.strftime('%Y-%m-%d %H:%M:%S')
                table.append([
                    '%s:%s/%s' % (user, owner, repo),
                    status, modified, error])
            print(tabulate(table))
        elif args.command == Command.PRINT:
            repo = tracker.load()
            print(repo)
        elif args.command == Command.GLORIFY:
            repo = tracker.load()
            glory = Glory(args.sourcerer_origin, args.sourcerer_api_origin)
            glory.make(repo)
        elif args.command == Command.CODE:
            if args.format == 'md':
                print(make_md_code(args.user, args.owner, args.repo))
            elif args.format == 'rst':
                print(make_rst_code(args.user, args.owner, args.repo))

    except Exception as e:
        print('e %s' % str(e))


if __name__ == '__main__':
    main()
