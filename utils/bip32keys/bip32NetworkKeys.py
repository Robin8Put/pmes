from bip32keys.bip32keys import Bip32Keys, decode_hex, encode_hex
import base58check
from hashlib import sha256


class Bip32NetworkKeys(Bip32Keys):

    private_key_magic_bytes = {'mainnet': '80', 'testnet': 'ef'}

    def __init__(self, init_params, mainnet=True):
        if 'wif' in init_params:
            self.wif = init_params['wif']
            super().__init__({'private_key': self.wif_to_private_key(init_params['wif'])})
        else:
            super().__init__(init_params)
            self.wif = Bip32NetworkKeys.private_key_to_wif(self.get_private_key(), mainnet)

    def get_wif(self):
        return self.wif

    @staticmethod
    def wif_to_private_key(wif):

        output = base58check.b58decode(wif)
        output = output[
                 1:-5]  # drop first network type byte, last 4 bytes checksum, 5-th from the end means that priv key is compressed
        return encode_hex(output)[0].decode()

    @staticmethod
    def private_key_to_wif(private_key, mainnet=True):
        output = Bip32NetworkKeys._validate_private_key_for_wif(private_key, mainnet)
        extended_private_key = output

        output = decode_hex(output)[0]
        checksum = sha256(sha256(output).digest()).hexdigest()[:8]

        output = extended_private_key + checksum

        output = decode_hex(output)[0]
        output = base58check.b58encode(output)

        return output.decode()

    @staticmethod
    def _validate_private_key_for_wif(private_key, mainnet):
        mb = Bip32NetworkKeys._get_private_key_magic_byte(mainnet)
        if len(private_key) == 64:
            return mb + private_key + '01'  # \x01 - compressed wif
        elif len(private_key) == 66:
            if private_key[0:2] == mb:
                return private_key + '01'
            elif private_key[-2:] == '01':
                return mb + private_key
        elif len(private_key) == 68:
            return private_key
        else:
            raise Exception('Bad private key length')

    @staticmethod
    def _get_private_key_magic_byte(mainnet):
        if mainnet:
            return Bip32NetworkKeys.private_key_magic_bytes['mainnet']
        else:
            return Bip32NetworkKeys.private_key_magic_bytes['testnet']


if __name__ == '__main__':
    keys = Bip32NetworkKeys({'wif': 'cRfsTP6CHgP53vvMGgdvE8tLBMs1Xdo2MQwMJtEqYTnKjWiCJrjC'}, mainnet=False)

    print('public key: ', keys.get_public_key())
    print('private key: ', keys.get_private_key())
    print('uncompressed public key: ', keys.get_uncompressed_public_key())
    print('wif: ', keys.get_wif())
    print('private key to wif: ', Bip32NetworkKeys.private_key_to_wif('7a6be1df9cc5d88edce5443ef0fce246123295dd82afae9a57986543272157cc', mainnet=False))