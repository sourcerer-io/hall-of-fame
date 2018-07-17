"""CLI for hall of fame.

Commands
    add: Adds a repo to track.
    delete: Deletes a tracked repo.
    list: Lists all tracked repos.
    update: Updates a repo.
"""

__copyright__ = '2018 Sourcerer, Inc.'
__author__ = 'Sergey Surkov'

import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str,
                        choices=['add', 'delete', 'list', 'update'],
                        help='Command to execute')
    parser.add_argument('--manager', type=str,
                        help='Github user that tracks a repo')
    parser.add_argument('--owner', type=str,
                        help='Github user that owns a repo')
    parser.add_argument('--repo', type=str,
                        help='Github repo name, excluding owner')
    args = parser.parse_args()

    if args.command in ['add', 'delete', 'update']:
        if not args.manager:
            parser.error('Must provide repo manager')
        if not args.owner:
            parser.error('Must provide repo owner')
        if not args.repo:
            parser.error('Must provide repo name')

    return args


def main():
    args = parse_args()


if __name__ == '__main__':
    main()
