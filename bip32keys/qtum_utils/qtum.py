from bip32keys.bip32addresses import Bip32Addresses


class Qtum(Bip32Addresses):

    def __init__(self, init_params, mainnet=True):
        super().__init__(init_params, Qtum._get_magic_byte(mainnet), mainnet)

    def get_qtum_address(self):
        return super().get_blockchain_address()

    @staticmethod
    def hex_to_qtum_address(hex_address, mainnet=True):
        return Bip32Addresses.hex_address_to_blockchain_address(hex_address, Qtum._get_magic_byte(mainnet))

    @staticmethod
    def public_key_to_qtum_address(public_key, mainnet=True):
        return Bip32Addresses.public_key_to_blockchain_address(public_key, Qtum._get_magic_byte(mainnet))

    @staticmethod
    def _get_magic_byte(mainnet):
        if mainnet:
            return '3a'
        else:
            return '78'

    @staticmethod
    def is_valid_qtum_address(address, mainnet=True):
        return Qtum.is_valid_address(address) and int(Qtum._get_magic_byte(mainnet), 16) == Qtum.get_magic_byte(address)


def test_address():
    q = Qtum("89324890413289043287943127894312789431241324132431243", mainnet=False)
    print('private key: ' + q.get_private_key())
    print('wif: ' + q.get_wif())
    print('public key: ' + q.get_public_key())
    print('uncompressed public key: ' + q.get_uncompressed_public_key())
    print('qtum address: ' + q.get_qtum_address())
    print('qtum hex address: ' + q.get_hex_address())
    print('pub_key to qtum address: ', Qtum.public_key_to_qtum_address('0356fd892d76117935853466db2bf0ac5d0eb9138bfa78c3b25d68f1b64f9a5106', mainnet=False))


def test_signature():

    q = Qtum('894389032980328902980324089324432432234324234', mainnet=False)
    public_key = q.get_uncompressed_public_key()
    private_key = q.get_private_key()
    message = 'hello'

    signature = Qtum.sign_message(message, private_key)
    print(Qtum.verify_message(message, signature, public_key))


if __name__ == '__main__':
    test_address()
    test_signature()
