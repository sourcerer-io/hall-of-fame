"""Google cloud storage implementation."""

__author__ = 'Sergey Surkov'
__copyright__ = '2018 Sourcerer, Inc'

from google.api_core.exceptions import NotFound
from google.cloud import storage as gstorage

from .storage_base import StorageBase


class GoogleCloudStorage(StorageBase):
    def __init__(self, bucket):
        self.client = gstorage.Client()
        self.bucket = self.client.get_bucket(bucket)

    def make_dirs(self, path):
        if not path.endswith('/'):
            path += '/'
        self.bucket.blob(path)

    def remove_file(self, path):
        try:
            self.bucket.delete_blob(path)
            return True
        except NotFound:
            return False

    def remove_subtree(self, path):
        if not path.endswith('/'):
            path += '/'
        blobs = list(self.bucket.list_blobs(prefix=path))
        self.bucket.delete_blobs(blobs)

    def list_dir(self, dir_path, include_files=True, include_subdirs=True):
        if dir_path and not dir_path.endswith('/'):
            dir_path += '/'
        blob_iter = self.bucket.list_blobs(prefix=dir_path, delimiter='/')
        files = list(blob_iter)  # Must do for actual API calls.
        subdirs = list(blob_iter.prefixes)

        result = []
        if include_files:
            result.extend([f.name for f in files])
        if include_subdirs:
            result.extend(subdirs)

        discard = len(dir_path)
        return [e[discard:].strip('/') for e in result]

    def path_exists(self, path):
        return self.bucket.get_blob(path) is not None

    def save_file(self, path, data, content_type='text/plain'):
        blob = self.bucket.blob(path)
        blob.upload_from_string(data, content_type=content_type)
 
    def load_file(self, path):
        blob = self.bucket.blob(path)
        return blob.download_as_string().decode()
