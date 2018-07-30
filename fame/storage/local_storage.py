"""Local storage implementation."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

import os
import shutil

from .storage_base import StorageBase

class LocalStorage(StorageBase):
    def __init__(self, work_dir):
        self.work_dir = work_dir

    def make_dirs(self, path):
        full_path = os.path.join(self.work_dir, path)
        os.makedirs(full_path, exist_ok=True)

    def remove_file(self, path):
        try:
            os.remove(path)
            return True
        except OSError:
            return False

    def remove_subtree(self, path):
        full_path = os.path.join(self.work_dir, path)
        shutil.rmtree(full_path, ignore_errors=True)

    def list_dir(self, dir_path, include_files=True, include_subdirs=True):
        full_path = os.path.join(self.work_dir, dir_path)
        result = []
        for entry in os.listdir(full_path):
            entry_path = os.path.join(full_path, entry)
            if not include_files and os.path.isfile(entry_path):
                continue
            if not include_subdirs and os.path.isdir(entry_path):
                continue

            result.append(entry)

        return result

    def path_exists(self, path):
        full_path = os.path.join(self.work_dir, path)
        return os.path.exists(full_path)

    def save_file(self, path, data, content_type='text/plain'):
        full_path = os.path.join(self.work_dir, path)
        with open(full_path, 'w') as f:
            f.write(data)

    def load_file(self, path):
        full_path = os.path.join(self.work_dir, path)
        with open(full_path, 'r') as f:
            return f.read()
