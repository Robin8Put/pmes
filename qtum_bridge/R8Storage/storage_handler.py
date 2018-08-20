from abc import abstractmethod, ABCMeta


class StorageHandler:
    __metaclass__ = ABCMeta

    @abstractmethod
    def upload_data(self, content):
        raise NotImplementedError()

    @abstractmethod
    def download_data(self, hash):
        raise NotImplementedError()



