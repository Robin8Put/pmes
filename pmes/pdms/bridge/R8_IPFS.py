import ipfsapi
from os import remove


class R8_IPFS:

    def __init__(self, ipfs_api=None):
        self.reload_ipfs(ipfs_api)

    def reload_ipfs(self, ipfs_api):
        if ipfs_api is None:
            self.ipfs_api = ipfsapi.connect('127.0.0.1', 5001)
        elif type(ipfs_api) is int:  # port specified
            self.ipfs_api = ipfsapi.connect('127.0.0.1', ipfs_api)
        else:
            self.ipfs_api = ipfs_api

    def upload_to_ipfs(self, my_content):
        file_name = 'temp.bak'

        with open(file_name, 'w') as ipfs_file:
            ipfs_file.write(R8_IPFS.encode_sc(my_content))

        ipfs_res = self.ipfs_api.add(file_name)  # accepts only files
        ipfs_hash = ipfs_res['Hash']
        #print('data: ' + my_content)
        #print('file name: ' + file_name)
        #print('ipfs hash: ' + ipfs_hash)

        remove(file_name)

        return ipfs_hash

    def version(self):
        return self.ipfs_api

    def download_from_ipfs(self, ipfs_hash):
        content = self.ipfs_api.cat(ipfs_hash)
        return R8_IPFS.decode_sc(content)

    def __getitem__(self, item):
        return self.download_from_ipfs(item)


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


if __name__=='__main__':
    encoded = R8_IPFS.encode_sc('This is content that will be uploaded to ipfs')
    print(encoded)
    decoded = R8_IPFS.decode_sc(encoded)
    print(decoded)

    data = 'ipfs is good'
    print('data: ', data)
    r8_ipfs = R8_IPFS()
    hash = r8_ipfs.upload_to_ipfs(data)
    print('hash: ', hash)
    print('downloaded data: ', r8_ipfs.download_from_ipfs(hash))