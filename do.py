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
    parser.parse_args()


def main():
    args = parse_args()


if __name__ == '__main__':
    main()
