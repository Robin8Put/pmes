from hashlib import sha256
from config import http_provider, ipc_path
from web3 import Web3, HTTPProvider, IPCProvider
from R8Blockchain.ethereumblockchain import EthereumBlockchain

import codecs

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


def test():
    str = 'hello'.encode()
    print(sha256(sha256(str).hexdigest().encode()).hexdigest())

def double_sha256(str):
    return sha256(sha256(str).hexdigest().encode()).hexdigest()

def verify_secret(*params, secret):
    str = ''
    for p in params:
        str += p
    str = str.encode()
    print(str)
    return double_sha256(str) == secret


if __name__=='__main__':
    w3 = Web3(IPCProvider(ipc_path))
    with open('/home/artem/.ethereum/rinkeby/keystore/UTC--2018-05-24T10-47-40.548612351Z--e630f8dd65f9be1ef2588da43c83b697a270d12e') as keyfile:
        encrypted_key = keyfile.read()
        private_key = w3.eth.account.decrypt(encrypted_key, 'eth2018')
        print(encode_hex(private_key)[0])
        # tip: do not save the key or password anywhere, especially into a shared source file


