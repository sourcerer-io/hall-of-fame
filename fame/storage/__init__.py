"""Local storage and Google cloud storage via common interface."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

from .storage import configure_for_local, configure_for_google_cloud
from .storage import (make_dirs, list_dir, file_exists, dir_exists,
                      last_modified, move_file, remove_file, remove_subtree,
                      save_file, load_file)

__all__ = ['configure_for_local', 'configure_for_google_cloud',
           'make_dirs', 'list_dir', 'file_exists', 'dir_exists',
           'last_modified', 'move_file', 'remove_file', 'remove_subtree',
           'save_file', 'load_file']
