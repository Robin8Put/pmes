import codecs
from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey, ellipticcurve
from ecdsa.ellipticcurve import Point, CurveFp
import ecdsa

from bip32utils import BIP32Key

import logging

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


class Bip32Keys:

    def __init__(self, init_params):
        if isinstance(init_params, str):
            self.init_from_entropy(init_params)
        elif isinstance(init_params, dict):
            if 'entropy' in init_params:
                self.init_from_entropy(init_params['entropy'])
            elif 'private_key' in init_params:
                self.init_from_private_key(init_params['private_key'])
            else:
                raise NotImplementedError()

    def init_from_entropy(self, entropy):
        entropy = entropy.encode()

        key = BIP32Key.fromEntropy(entropy, public=False)
        self.private_key = key.PrivateKey()
        self.public_key = key.PublicKey()

        self.uncompressed_public_key = decode_hex(Bip32Keys.to_uncompressed_public_key(
            self.get_public_key()
        ))[0]

    def init_from_private_key(self, private_key):
        sk = SigningKey.from_string(string=decode_hex(private_key)[0], curve=ecdsa.SECP256k1, hashfunc=sha256)
        vk = sk.get_verifying_key()

        self.private_key = sk.to_string()
        self.public_key = decode_hex(Bip32Keys.to_compressed_public_key(encode_hex(vk.to_string())[0].decode()))[0]
        self.uncompressed_public_key = b'\x04' + vk.to_string()

    def get_public_key(self):
        return encode_hex(self.public_key)[0].decode()

    def get_private_key(self):
        return encode_hex(self.private_key)[0].decode()

    def get_uncompressed_public_key(self):
        return encode_hex(self.uncompressed_public_key)[0].decode()

    def sign_msg(self, message):
        return Bip32Keys.sign_message(message, self.get_private_key())

    def verify_msg(self, message, signature):
        return Bip32Keys.verify_message(message, signature, self.get_uncompressed_public_key())

    @staticmethod
    def to_uncompressed_public_key(public_key):
        if len(public_key) == 130:
            return public_key
        elif len(public_key) == 128:
            return '04' + public_key
        p_hex = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F'
        p = int(p_hex, 16)

        x_hex = public_key[2:66]
        x = int(x_hex, 16)
        prefix = public_key[0:2]

        y_square = (pow(x, 3, p) + 7) % p
        y_square_square_root = pow(y_square, (p + 1) // 4, p)
        if (prefix == "02" and y_square_square_root & 1) or (prefix == "03" and not y_square_square_root & 1):
            y = (-y_square_square_root) % p
        else:
            y = y_square_square_root

        computed_y_hex = format(y, '064x')
        computed_uncompressed_key = "04" + x_hex + computed_y_hex

        return computed_uncompressed_key

    @staticmethod
    def to_compressed_public_key(public_key):
        if len(public_key) == 66:
            return public_key

        y_hex = public_key[64:]
        if int(y_hex, 16) & 1:
            prefix = '03'
        else:
            prefix = '02'

        if len(public_key) == 130:
            return prefix + public_key[2:66]
        elif len(public_key) == 128:
            return prefix + public_key[:64]

    @staticmethod
    def sign_message(message, private_key):
        priv_key = Bip32Keys._validate_private_key_for_signature(private_key)
        message = message.encode()
        sk = SigningKey.from_string(curve=ecdsa.SECP256k1, string=decode_hex(priv_key)[0], hashfunc=sha256)
        sig = sk.sign(message, sigencode=ecdsa.util.sigencode_der)
        return encode_hex(sig)[0].decode()

    @staticmethod
    def verify_message(message, signature, public_key):
        pub_key = Bip32Keys._validate_public_key_for_signature(public_key)
        sig = signature
        msg = message.encode()
        vk = VerifyingKey.from_string(string=decode_hex(pub_key)[0], curve=ecdsa.SECP256k1, hashfunc=sha256)

        if len(sig) == 128:
            vk.verify(decode_hex(sig)[0], msg, sigdecode=ecdsa.util.sigdecode_string)
        else:
            vk.verify(decode_hex(sig)[0], msg, sigdecode=ecdsa.util.sigdecode_der)

        return True

    @staticmethod
    def _validate_private_key_for_signature(private_key):
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
    def _validate_public_key_for_signature(public_key):
        if len(public_key) == 128:
            return public_key
        elif len(public_key) == 130:
            return public_key[2:]
        elif len(public_key) == 66:
            return Bip32Keys.to_uncompressed_public_key(public_key)[2:]
        else:
            raise Exception('Unsupported public key format')


    """
    for asymetric encryption
    """
    # Certicom secp256-k1
    _a = 0x0000000000000000000000000000000000000000000000000000000000000000
    _b = 0x0000000000000000000000000000000000000000000000000000000000000007
    _p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    _Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    _Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    _r = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

    curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
    generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)

    def get_shared_key(self, another_public_key):
        return Bip32Keys.generate_shared_key(self.get_private_key(), another_public_key)

    @staticmethod
    def generate_shared_key(private_key, public_key):
        public_key = Bip32Keys.to_uncompressed_public_key(public_key)
        private_key = int(private_key, 16)
        x = int(public_key[2:66], 16)  # drop prefix
        y = int(public_key[-64:], 16)
        another_point = Point(Bip32Keys.curve_secp256k1, x, y)
        shared_point = another_point * private_key
        return str(hex(shared_point.x()))[2:] + str(hex(shared_point.y()))[2:]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    keys = Bip32Keys({'entropy': '3123213213213123312c3kjifj3'})
    print('public key: ', keys.get_public_key())
    print('private key: ', keys.get_private_key())
    print('uncompressed public key: ', keys.get_uncompressed_public_key())
    sig = keys.sign_msg('hello world')
    print('signature: ', sig)
    print('verify signature: ', keys.verify_msg('hello world', sig))

    print('compressed: ', Bip32Keys.to_compressed_public_key('041ad7138370ef5e93fb243aff3373e2b92383818dfc20022841b655e0cd6c618cd578261c78e1adfe205c3ade8b81e1722d6058be9155eee55468fbb04b62040e'))

    keys2 = Bip32Keys({'entropy': 'fdjsofjioej9fsdfjdskfdsjkhfdsj'})
    print('shared key', keys2.get_shared_key(keys.get_public_key()))
    print('shared key', keys.get_shared_key(keys2.get_public_key()))
    print('shared key', Bip32Keys.generate_shared_key(keys.get_private_key(), keys2.get_public_key()))
