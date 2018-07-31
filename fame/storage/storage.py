"""Local storage and Google cloud storage via common interface."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

from .local_storage import LocalStorage
from .google_cloud_storage import GoogleCloudStorage

storage = None


def configure_for_local(work_dir):
    global storage
    storage = LocalStorage(work_dir)


def configure_for_google_cloud(bucket):
    global storage
    storage = GoogleCloudStorage(bucket)


def make_dirs(path):
    """Makes all directories in a path."""
    if not storage:
        error('Storage not initialized')
    return storage.make_dirs(path)


def remove_file(path):
    """Removes a file."""
    if not storage:
        error('Storage not initialized')
    return storage.remove_file(path)


def remove_subtree(path):
    """Deletes directory and all its contents."""
    if not storage:
        error('Storage not initialized')
    return storage.remove_subtree(path)


def list_dir(dir_path, include_files=True, include_subdirs=True):
    if not storage:
        error('Storage not initialized')
    return storage.list_dir(dir_path, include_files, include_subdirs)


def file_exists(file_path):
    if not storage:
        error('Storage not initialized')
    return storage.file_exists(file_path)


def dir_exists(dir_path):
    if not storage:
        error('Storage not initialized')
    return storage.dir_exists(dir_path)


def save_file(path, data, content_type='text/plain'):
    if not storage:
        error('Storage not initialized')
    return storage.save_file(path, data, content_type)


def load_file(path):
    if not storage:
        error('Storage not initialized')
    return storage.load_file(path)


class StorageError(Exception):
    def __init__(self, message):
        super().__init__(message)


def error(message):
    raise StorageError(message)
