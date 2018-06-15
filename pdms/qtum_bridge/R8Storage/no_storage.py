from R8Storage.storage_handler import StorageHandler


class NoStorage(StorageHandler):

    def download_data(self, hash):
        return hash

    def upload_data(self, content):
        return content