import ipfsapi
import signal
from R8Storage.storage_handler import StorageHandler
from os import remove
from contextlib import contextmanager


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise Exception("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class IpfsStorage(StorageHandler):

    def __init__(self, ipfs_api=None, time_limit=1):
        if ipfs_api is None:
            self.ipfs_api = ipfsapi.connect('127.0.0.1', 5001)
        else:
            self.ipfs_api = ipfs_api

        self.time_limit = time_limit

    @classmethod
    def from_host_port(cls, host='127.0.0.1', port=5001, time_limit=1):
        return cls(ipfsapi.connect(host, port), time_limit)

    def reload_http_provider(self, host, port):
        self.ipfs_api = ipfsapi.connect(host, port)

    def upload_data(self, content):
        file_name = 'temp.bak'

        with open(file_name, 'w') as ipfs_file:
            ipfs_file.write(IpfsStorage.encode_sc(content))

        ipfs_res = self.ipfs_api.add(file_name)  # accepts only files
        ipfs_hash = ipfs_res['Hash']
        # print('data: ' + my_content)
        # print('file name: ' + file_name)
        # print('ipfs hash: ' + ipfs_hash)

        remove(file_name)

        return ipfs_hash

    def version(self):
        return self.ipfs_api

    def download_data(self, ipfs_hash):
        with time_limit(self.time_limit):
            content = self.ipfs_api.cat(ipfs_hash)
        return IpfsStorage.decode_sc(content)

    def set_time_limit(self, time_limit):
        self.time_limit = time_limit

    def get_time_limit(self):
        return self.time_limit

    def __getitem__(self, item):
        return self.download_data(item)

    @staticmethod
    def encode_sc(raw_data):
        hex_len = format(len(raw_data), '02x').rjust(8, '0')
        return hex_len + raw_data

    @staticmethod
    def decode_sc(ipfs_data):
        if ipfs_data[0:3] == b'000' or ipfs_data[0:3] == '000':  # check if was encoded
            hexlen = ipfs_data[0:8]
            raw_data = ipfs_data[8:int(hexlen, 16)+8]
            return raw_data
        else:
            return ipfs_data


if __name__ == '__main__':
    encoded = IpfsStorage.encode_sc('This is content that will be uploaded to ipfs')
    print(encoded)
    decoded = IpfsStorage.decode_sc(encoded)
    print(decoded)

    data = 'ipfs is good'
    print('data: ', data)
    r8_ipfs = IpfsStorage()
    hash = r8_ipfs.upload_data(data)
    print('hash: ', hash)
    print('downloaded data: ', r8_ipfs.download_data('QmSxS1rgboA8UUH3WN3ih9K4YYRJEsDdyMuAqFxd25Dh2p'))
