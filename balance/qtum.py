import hashlib
from hashlib import sha256
import codecs
import binascii
import base58check
from ecdsa import SigningKey, VerifyingKey
import ecdsa
from ecdsa.util import PRNG

from bip32utils import BIP32Key


class Qtum:
    def __init__(self, entropy):  # todo: init from private key
        entropy = entropy.encode()

        self.decode_hex = codecs.getdecoder("hex_codec")
        self.encode_hex = codecs.getencoder("hex_codec")

        key = BIP32Key.fromEntropy(entropy, public=False)
        private_key = key.PrivateKey()
        public_key = key.PublicKey()
        wif = key.WalletImportFormat()

        sk = SigningKey.from_string(string=private_key, curve=ecdsa.SECP256k1, hashfunc=sha256)
        vk = sk.get_verifying_key()
        #print(public_key)

        output = sha256(public_key).digest()
        #print(binascii.hexlify(output))

        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(output)
        output = binascii.hexlify(ripemd160.digest())
        #print(output)

        output = b'3A' + output  # 3A is magic byte
        extended_ripmd160 = output
        #print(output)

        output = self.decode_hex(output)[0]
        output = sha256(output).digest()
        #print(binascii.hexlify(output))

        output = sha256(output).hexdigest().encode()
        #print(binascii.hexlify(output))

        checksum = output[:8]
        #print(checksum)

        output = extended_ripmd160 + checksum
        #print(output)

        output = self.decode_hex(output)[0]
        output = base58check.b58encode(output)
        #print(output)

        self.wif = wif
        self.private_key = private_key
        self.public_key = public_key
        self.uncompressed_public_key = vk.to_string()
        self.qtum_address = output

    def get_uncompressed_public_key(self):
        return self.encode_hex(self.uncompressed_public_key)[0].decode()

    def get_public_key(self):
        return self.encode_hex(self.public_key)[0].decode()

    def get_private_key(self):
        return self.encode_hex(self.private_key)[0].decode()

    def get_qtum_address(self):
        return self.qtum_address.decode()

    def get_wif(self):
        return self.wif

    @staticmethod
    def get_magic_byte(address):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        output = base58check.b58decode(address)
        output = encode_hex(output)[0].decode()

        return int(output[0:2], 16)


    @staticmethod
    def is_valid_address(address):
        try:
            decode_hex = codecs.getdecoder("hex_codec")
            encode_hex = codecs.getencoder("hex_codec")
            output = base58check.b58decode(address)
            output = encode_hex(output)[0].decode()

            checksum = output[-8:]
            extended_ripmd160 = output[:-8]

            output = decode_hex(extended_ripmd160)[0]
            output = sha256(sha256(output).digest()).hexdigest()[0:8]

            return checksum == output
        except Exception:
            return False

    @staticmethod
    def validate_private_key_for_wif(private_key):
        if len(private_key) == 64:
            return '80' + private_key + '01'  # \x80 - network mainnet, \x01 - compressed wif
        elif len(private_key) == 66:
            if private_key[0:2] == '80':
                return '80' + private_key
            elif private_key[-2:] == '01':
                return private_key + '01'
        elif len(private_key) == 68:
            return private_key
        else:
            raise Exception('Bad private key length')

    @staticmethod
    def validate_private_key_for_signature(private_key):
        if len(private_key) == 64:
            return private_key
        elif len(private_key) == 66:
            if private_key[0:2] == '80':
                return private_key[2:]
            elif private_key[-2:] == '01':
                return private_key[:-2]
        elif len(private_key) == 68:
            return private_key[2:-2]
        else:
            raise Exception('Bad private key length')

    @staticmethod
    def private_key_to_wif(private_key):

        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")

        output = Qtum.validate_private_key_for_wif(private_key)
        extended_private_key = output
        #print(output)

        output = decode_hex(output)[0]
        output = sha256(output).digest()
        #print(encode_hex(output)[0])

        output = sha256(output).digest()
        #print(encode_hex(output)[0])

        output = encode_hex(output)[0]
        checksum = output[:8]
        output = extended_private_key + checksum.decode()
        #print(output)

        output = decode_hex(output)[0]
        #print('my_raw:' + str(output))
        output = base58check.b58encode(output)
        #print(output)

        return output.decode()

    @staticmethod
    def wif_to_private_key(wif):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")

        output = base58check.b58decode(wif)
        #print(output)
        output = output[1:-5] # drop first network type byte, last 4 bytes checksum, 5-th from the end means that priv key is compressed
        #print(output)
        return encode_hex(output)[0].decode()


    @staticmethod
    def sign_message(message, private_key):
        priv_key = Qtum.validate_private_key_for_signature(private_key)
        message = message.encode()
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        sk = SigningKey.from_string(curve=ecdsa.SECP256k1, string=decode_hex(priv_key)[0], hashfunc=sha256)
        sig = sk.sign(message)
        return encode_hex(sig)[0].decode()


    @staticmethod
    def validate_public_key_for_signature(public_key):
        if len(public_key) == 128:
            return public_key
        elif len(public_key) == 130:
            return public_key[2:]
        else:
            raise Exception('Unsupported public key format')  # todo: retrive uncompressed public key from compressed public key

    @staticmethod
    def validate_signature(signature):
        if len(signature) == 128:
            return signature
        elif len(signature) == 140:
            return signature[8:72] + signature[-64:]
        else:
            raise Exception('Unsupported signature format')

    @staticmethod
    def verify_message(message, signature, public_key):
        pub_key = Qtum.validate_public_key_for_signature(public_key)
        sig = Qtum.validate_signature(signature)
        message = message.encode()
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        vk = VerifyingKey.from_string(string=decode_hex(pub_key)[0], curve=ecdsa.SECP256k1, hashfunc=sha256)
        try:
            vk.verify(decode_hex(sig)[0], message)
        except:
            return False
        return True


def test_address():
    q = Qtum("3123213213213123312c3kjifj3")
    print('private key: ' + q.get_private_key())
    print('wif: ' + q.get_wif())
    print('public key: ' + q.get_public_key())
    print('uncompressed public key: ' + q.get_uncompressed_public_key())
    print('qtum address: ' + q.get_qtum_address())
    print('my wif: ' + Qtum.private_key_to_wif('7a6be1df9cc5d88edce5443ef0fce246123295dd82afae9a57986543272157cc'))
    print('wif to private key: ' + Qtum.wif_to_private_key('L1KgWtY57mSggocxDVSDRGvLVCRYuQfj8ur7cHvuv6UkgJmXweti'))

    print(Qtum.get_magic_byte('QLonXSbmVhECBV3fqN3L7H9LJn8jUS3m9k'))
    print(Qtum.is_valid_address('QLonXSbmVhECBV3fqN3L7H9LJn8jUS3m9k'))


def test_signature():
    decode_hex = codecs.getdecoder("hex_codec")
    encode_hex = codecs.getencoder("hex_codec")

    q = Qtum('1232131234324324324234321231')
    public_key = q.get_uncompressed_public_key()
    private_key = q.get_private_key()
    message = 'hello'

    signature = Qtum.sign_message(message, private_key)
    print(Qtum.verify_message(message, signature, public_key))


if __name__ == '__main__':
    test_address()
    test_signature()