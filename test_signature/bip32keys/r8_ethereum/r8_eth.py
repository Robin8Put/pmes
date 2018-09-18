from bip32keys.bip32keys import Bip32Keys, decode_hex, encode_hex
import sha3
from web3 import Web3


class R8_Ethereum(Bip32Keys):

    def __init__(self, params):
        super().__init__(params)
        self.address = R8_Ethereum.public_key_to_checksum_address(self.get_uncompressed_public_key())

    def get_address(self):
        return self.address


    @staticmethod
    def public_key_to_ethereum_address(public_key):
        public_key = Bip32Keys.to_uncompressed_public_key(public_key)[2:]  # drop pub key version byte
        k = sha3.keccak_256()
        k.update(decode_hex(public_key)[0])
        hash = k.hexdigest()
        return hash[24:]

    @staticmethod
    def public_key_to_checksum_address(public_key):
        return Web3.toChecksumAddress(R8_Ethereum.public_key_to_ethereum_address(public_key))[2:]

    @staticmethod
    def to_checksum_address(address):
        return Web3.toChecksumAddress(address)


if __name__ == '__main__':
    eth = R8_Ethereum({'private_key': '8fd5de0f76ed11e9faafc27e031e31debc360241817b12faf18e708edf1de0df'})
    print(eth.get_address())