from R8Storage.ipfs_storage import IpfsStorage
from R8Storage.no_storage import NoStorage


class R8Storage:
    def __init__(self, storage_handler=None):
        if storage_handler is None:
            self.handler = NoStorage()
        else:
            self.handler = storage_handler

    @classmethod
    def init_ipfs(cls, host='127.0.0.1', port=5001, time_limit=1):
        return cls(IpfsStorage.from_host_port(host, port, time_limit))

    @classmethod
    def init_no_storage(cls):
        return cls(NoStorage())

    def download_content(self, hash):
        return self.handler.download_data(hash)

    def upload_content(self, content):
        return self.handler.upload_data(content)


if __name__ == '__main__':
    storage = R8Storage.init_ipfs()

    print(storage.upload_content('test'))
    print(storage.download_content('QmZWUWexr2Kyg5y6JB1osTF8Gn5xAHmKzRYwfFpT1Xm3gT'))
