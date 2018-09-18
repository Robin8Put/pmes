from OpenSSL import crypto
import json
import pickle
import codecs

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


class SignatureValidator:

    def __init__(self, private_key, public_key):
        self.private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key)
        self.public_key = crypto.load_publickey(crypto.FILETYPE_PEM, public_key)
        self.cert = crypto.X509()
        self.cert.set_pubkey(self.public_key)

    def verify(self, params):
        # params - json
        # raise exception if signature is invalid
        message = params['message']
        signature = decode_hex(params['signature'])[0]

        crypto.verify(self.cert, signature, message, 'sha256')

    def sign(self, params):
        # params - json
        # returns dict (message, signature)
        dumped_json = encode_hex(
            pickle.dumps(params)
        )[0].decode()

        signature = encode_hex(
            crypto.sign(self.private_key, dumped_json, 'sha256')
        )[0].decode()

        return {'message': dumped_json, 'signature': signature}

    @staticmethod
    def json_to_hex(params):
        dumped_json = encode_hex(
            pickle.dumps(params)
        )[0].decode()
        return dumped_json

    @staticmethod
    def hex_to_json(dumped_json):
        loaded_json = pickle.loads(
            decode_hex(dumped_json)[0]
        )
        return loaded_json
