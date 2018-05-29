import os
import hmac
import hashlib
import ecdsa
import struct
import codecs
import json
import random
from ecdsa.curves import SECP256k1
from ecdsa.ecdsa import int_to_string, string_to_int
from ecdsa.numbertheory import square_root_mod_prime as sqrt_mod
import time
import datetime
import requests
import codecs
import hashlib
from hashlib import sha256
from ecdsa import SigningKey, VerifyingKey
import ecdsa
import logging

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


__base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__base58_alphabet_bytes = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__base58_radix = len(__base58_alphabet)


def get_time_stamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')


def __string_to_int(data):
    "Convert string of bytes Python integer, MSB"
    val = 0
   
    # Python 2.x compatibility
    if type(data) == str:
        data = bytearray(data)

    for (i, c) in enumerate(data[::-1]):
        val += (256**i)*c
    return val


def encode(data):
    "Encode bytes into Bitcoin base58 string"
    enc = ''
    val = __string_to_int(data)
    while val >= __base58_radix:
        val, mod = divmod(val, __base58_radix)
        enc = __base58_alphabet[mod] + enc
    if val:
        enc = __base58_alphabet[val] + enc

    # Pad for leading zeroes
    n = len(data)-len(data.lstrip(b'\0'))
    return __base58_alphabet[0]*n + enc


def check_encode(raw):
    "Encode raw bytes into Bitcoin base58 string with checksum"
    chk = sha256(sha256(raw).digest()).digest()[:4]
    return encode(raw+chk)


def decode(data):
    "Decode Bitcoin base58 format string to bytes"
    # Python 2.x compatability
    if bytes != str:
        data = bytes(data, 'ascii')

    val = 0
    for (i, c) in enumerate(data[::-1]):
        val += __base58_alphabet_bytes.find(c) * (__base58_radix**i)

    dec = bytearray()
    while val >= 256:
        val, mod = divmod(val, 256)
        dec.append(mod)
    if val:
        dec.append(val)

    return bytes(dec[::-1])


def check_decode(enc):
    "Decode bytes from Bitcoin base58 string and test checksum"
    dec = decode(enc)
    raw, chk = dec[:-4], dec[-4:]
    if chk != sha256(sha256(raw).digest()).digest()[:4]:
        raise ValueError("base58 decoding checksum error")
    else:
        return raw




MIN_ENTROPY_LEN = 128        # bits
BIP32_HARDEN    = 0x80000000 # choose from hardened set of child keys
CURVE_GEN       = ecdsa.ecdsa.generator_secp256k1
CURVE_ORDER     = CURVE_GEN.order()
FIELD_ORDER     = SECP256k1.curve.p()
INFINITY        = ecdsa.ellipticcurve.INFINITY
EX_MAIN_PRIVATE = codecs.decode('0488ade4', 'hex') # Version string for mainnet extended private keys
EX_MAIN_PUBLIC  = codecs.decode('0488b21e', 'hex') # Version string for mainnet extended public keys
EX_TEST_PRIVATE = codecs.decode('04358394', 'hex') # Version string for testnet extended private keys
EX_TEST_PUBLIC  = codecs.decode('043587CF', 'hex') # Version string for testnet extended public keys

class BIP32Key(object):

    # Static initializers to create from entropy or external formats
    #
    @staticmethod
    def fromEntropy(entropy, public=False, testnet=False):
        "Create a BIP32Key using supplied entropy >= MIN_ENTROPY_LEN"
        if entropy == None:
            entropy = os.urandom(MIN_ENTROPY_LEN/8) # Python doesn't have os.random()
        if not len(entropy) >= MIN_ENTROPY_LEN/8:
            raise ValueError("Initial entropy %i must be at least %i bits" %
                                (len(entropy), MIN_ENTROPY_LEN))
        I = hmac.new(b"Bitcoin seed", entropy, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]
        # FIXME test Il for 0 or less than SECP256k1 prime field order
        key = BIP32Key(secret=Il, chain=Ir, depth=0, index=0, fpr=b'\0\0\0\0', public=False, testnet=testnet)
        if public:
            key.SetPublic()
        return key

    @staticmethod
    def fromExtendedKey(xkey, public=False):
        """
        Create a BIP32Key by importing from extended private or public key string

        If public is True, return a public-only key regardless of input type.
        """
        # Sanity checks
        raw = Base58.check_decode(xkey)
        if len(raw) != 78:
            raise ValueError("extended key format wrong length")

        # Verify address version/type
        version = raw[:4]
        if version == EX_MAIN_PRIVATE:
            is_testnet = False
            is_pubkey = False
        elif version == EX_TEST_PRIVATE:
            is_testnet = True
            is_pubkey = False
        elif version == EX_MAIN_PUBLIC:
            is_testnet = False
            is_pubkey = True
        elif version == EX_TEST_PUBLIC:
            is_testnet = True
            is_pubkey = True
        else:
            raise ValueError("unknown extended key version")

        # Extract remaining fields
        # Python 2.x compatibility
        if type(raw[4]) == int:
            depth = raw[4]
        else:
            depth = ord(raw[4])
        fpr = raw[5:9]
        child = struct.unpack(">L", raw[9:13])[0]
        chain = raw[13:45]
        secret = raw[45:78]

        # Extract private key or public key point
        if not is_pubkey:
            secret = secret[1:]
        else:
            # Recover public curve point from compressed key
            # Python3 FIX
            lsb = secret[0] & 1 if type(secret[0]) == int else ord(secret[0]) & 1
            x = string_to_int(secret[1:])
            ys = (x**3+7) % FIELD_ORDER # y^2 = x^3 + 7 mod p
            y = sqrt_mod(ys, FIELD_ORDER)
            if y & 1 != lsb:
                y = FIELD_ORDER-y
            point = ecdsa.ellipticcurve.Point(SECP256k1.curve, x, y)
            secret = ecdsa.VerifyingKey.from_public_point(point, curve=SECP256k1)

        key = BIP32Key(secret=secret, chain=chain, depth=depth, index=child, fpr=fpr, public=is_pubkey, testnet=is_testnet)
        if not is_pubkey and public:
            key = key.SetPublic()
        return key


    # Normal class initializer
    def __init__(self, secret, chain, depth, index, fpr, public=False, testnet=False):
        """
        Create a public or private BIP32Key using key material and chain code.

        secret   This is the source material to generate the keypair, either a
                 32-byte string representation of a private key, or the ECDSA
                 library object representing a public key.

        chain    This is a 32-byte string representation of the chain code

        depth    Child depth; parent increments its own by one when assigning this

        index    Child index

        fpr      Parent fingerprint

        public   If true, this keypair will only contain a public key and can only create
                 a public key chain.
        """

        self.public = public
        if public is False:
            self.k = ecdsa.SigningKey.from_string(secret, curve=SECP256k1)
            self.K = self.k.get_verifying_key()
        else:
            self.k = None
            self.K = secret

        self.C = chain
        self.depth = depth
        self.index = index
        self.parent_fpr = fpr
        self.testnet = testnet


    # Internal methods not intended to be called externally
    #
    def hmac(self, data):
        """
        Calculate the HMAC-SHA512 of input data using the chain code as key.

        Returns a tuple of the left and right halves of the HMAC
        """         
        I = hmac.new(self.C, data, hashlib.sha512).digest()
        return (I[:32], I[32:])


    def CKDpriv(self, i):
        """
        Create a child key of index 'i'.

        If the most significant bit of 'i' is set, then select from the
        hardened key set, otherwise, select a regular child key.

        Returns a BIP32Key constructed with the child key parameters,
        or None if i index would result in an invalid key.
        """
        # Index as bytes, BE
        i_str = struct.pack(">L", i)

        # Data to HMAC
        if i & BIP32_HARDEN:
            data = b'\0' + self.k.to_string() + i_str
        else:
            data = self.PublicKey() + i_str
        # Get HMAC of data
        (Il, Ir) = self.hmac(data)

        # Construct new key material from Il and current private key
        Il_int = string_to_int(Il)
        if Il_int > CURVE_ORDER:
            return None
        pvt_int = string_to_int(self.k.to_string())
        k_int = (Il_int + pvt_int) % CURVE_ORDER
        if (k_int == 0):
            return None
        secret = (b'\0'*32 + int_to_string(k_int))[-32:]
        
        # Construct and return a new BIP32Key
        return BIP32Key(secret=secret, chain=Ir, depth=self.depth+1, index=i, fpr=self.Fingerprint(), public=False, testnet=self.testnet)


    def CKDpub(self, i):
        """
        Create a publicly derived child key of index 'i'.

        If the most significant bit of 'i' is set, this is
        an error.

        Returns a BIP32Key constructed with the child key parameters,
        or None if index would result in invalid key.
        """

        if i & BIP32_HARDEN:
            raise Exception("Cannot create a hardened child key using public child derivation")

        # Data to HMAC.  Same as CKDpriv() for public child key.
        data = self.PublicKey() + struct.pack(">L", i)

        # Get HMAC of data
        (Il, Ir) = self.hmac(data)

        # Construct curve point Il*G+K
        Il_int = string_to_int(Il)
        if Il_int >= CURVE_ORDER:
            return None
        point = Il_int*CURVE_GEN + self.K.pubkey.point
        if point == INFINITY:
            return None

        # Retrieve public key based on curve point
        K_i = ecdsa.VerifyingKey.from_public_point(point, curve=SECP256k1)

        # Construct and return a new BIP32Key
        return BIP32Key(secret=K_i, chain=Ir, depth=self.depth+1, index=i, fpr=self.Fingerprint(), public=True, testnet=self.testnet)


    # Public methods
    #
    def ChildKey(self, i):
        """
        Create and return a child key of this one at index 'i'.

        The index 'i' should be summed with BIP32_HARDEN to indicate
        to use the private derivation algorithm.
        """
        if self.public is False:
            return self.CKDpriv(i)
        else:
            return self.CKDpub(i)


    def SetPublic(self):
        "Convert a private BIP32Key into a public one"
        self.k = None
        self.public = True


    def PrivateKey(self):
        "Return private key as string"
        if self.public:
            raise Exception("Publicly derived deterministic keys have no private half")
        else:
            return self.k.to_string()


    def PublicKey(self):
        "Return compressed public key encoding"
        padx = (b'\0'*32 + int_to_string(self.K.pubkey.point.x()))[-32:]
        if self.K.pubkey.point.y() & 1:
            ck = b'\3'+padx
        else:
            ck = b'\2'+padx
        return ck


    def ChainCode(self):
        "Return chain code as string"
        return self.C


    def Identifier(self):
        "Return key identifier as string"
        cK = self.PublicKey()
        return hashlib.new('ripemd160', sha256(cK).digest()).digest()


    def Fingerprint(self):
        "Return key fingerprint as string"
        return self.Identifier()[:4]


    def Address(self):
        "Return compressed public key address"
        addressversion = b'\x00' if not self.testnet else b'\x6f'
        vh160 = addressversion + self.Identifier()
        return Base58.check_encode(vh160)


    def WalletImportFormat(self):
        "Returns private key encoded for wallet import"
        if self.public:
            raise Exception("Publicly derived deterministic keys have no private half")
        addressversion = b'\x80' if not self.testnet else b'\xef'
        raw = addressversion + self.k.to_string() + b'\x01' # Always compressed
        return Base58.check_encode(raw)


    def ExtendedKey(self, private=True, encoded=True):
        "Return extended private or public key as string, optionally Base58 encoded"
        if self.public is True and private is True:
            raise Exception("Cannot export an extended private key from a public-only deterministic key")
        if not self.testnet:
            version = EX_MAIN_PRIVATE if private else EX_MAIN_PUBLIC
        else:
            version = EX_TEST_PRIVATE if private else EX_TEST_PUBLIC
        depth = bytes(bytearray([self.depth]))
        fpr = self.parent_fpr
        child = struct.pack('>L', self.index)
        chain = self.C
        if self.public is True or private is False:
            data = self.PublicKey()
        else:
            data = b'\x00' + self.PrivateKey()
        raw = version+depth+fpr+child+chain+data
        if not encoded:
            return raw
        else:
            return Base58.check_encode(raw)

    # Debugging methods
    #
    def dump(self):
        "Dump key fields mimicking the BIP0032 test vector format"
        print("   * Identifier")
        print("     * (hex):      ", self.Identifier().encode('hex'))
        print("     * (fpr):      ", self.Fingerprint().encode('hex'))
        print("     * (main addr):", self.Address())
        if self.public is False:
            print("   * Secret key")
            print("     * (hex):      ", self.PrivateKey().encode('hex'))
            print("     * (wif):      ", self.WalletImportFormat())
        print("   * Public key")
        print("     * (hex):      ", self.PublicKey().encode('hex'))
        print("   * Chain code")
        print("     * (hex):      ", self.C.encode('hex'))
        print("   * Serialized")
        print("     * (pub hex):  ", self.ExtendedKey(private=False, encoded=False).encode('hex'))
        print("     * (prv hex):  ", self.ExtendedKey(private=True, encoded=False).encode('hex'))
        print("     * (pub b58):  ", self.ExtendedKey(private=False, encoded=True))
        print("     * (prv b58):  ", self.ExtendedKey(private=True, encoded=True))



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
        sig = sk.sign(message)
        return encode_hex(sig)[0].decode()

    @staticmethod
    def verify_message(message, signature, public_key):
        pub_key = Bip32Keys._validate_public_key_for_signature(public_key)
        sig = Bip32Keys._validate_signature(signature)
        msg = message.encode()
        vk = VerifyingKey.from_string(string=decode_hex(pub_key)[0], curve=ecdsa.SECP256k1, hashfunc=sha256)

        try:
            vk.verify(decode_hex(sig)[0], msg)
        except:
            return False
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

    @staticmethod
    def _validate_signature(signature):
        if len(signature) == 128:
            return signature
        elif len(signature) == 140:
            return signature[8:72] + signature[-64:]
        else:
            raise Exception('Unsupported signature format')




class PMESClient(object):
    def __init__(self, host="http://127.0.0.1:8000", storagehost="http://127.0.0.1:8001"):
        #self.host = "http://176.31.125.26:8000"
        #self.host = "http://127.0.0.1:8000"
        self.host = host
        self.storagehost = storagehost


    @classmethod
    def _get_time_stamp(cls):
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')


    @classmethod
    def _make_message(cls, data={}):
        data["timestamp"] = PMESClient._get_time_stamp() 
        return json.dumps(data)


    def gen_keys(self):
        with open("generated.json") as generated:
            keys = random.choice(json.load(generated))
        with open("keys.json", "w") as keyfile:
            keyfile.write(json.dumps(keys))
        print("Generating keys for you...")
        time.sleep(2)
        print("Done!")
        print("It saved at 'keys.json' file.")



    def fill_form(self):
        with open("account.json", "w") as accountfile:
            while True:
                email = input("Insert your e-mail (required): ")
                if email:
                    break
            while True:
                device_id = input("Insert your device id (required): ")
                if device_id:
                    break
            phone = input("Insert your phone (optional): ")
            data = {"email":email, "device_id":device_id}
            if phone:
                data.update({"phone":phone})
            accountfile.write(json.dumps(data))
            print("Your account data submited.")



    def create_account(self):
        endpoint = input("Insert url address ('/api/accounts' by default): ") or "/api/accounts"
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        message = PMESClient._make_message({
                "email":account["email"],
                "device_id":account["device_id"]
            })
        data = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"]),
            "email": account["email"],
            "device_id": account["device_id"]
        }
        url = "%s%s" % (self.host, endpoint)
        print("\nPOST request to %s\n" % url)
        time.sleep(2)
        request = requests.post(url, data=data)
        try:
            return request.json()
        except:
            return request.text


    def get_account_data(self):
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        endpoint = input("Insert your account address ('/api/accounts/%s') by default: " % keys["public_key"]) or "/api/accounts/%s" % keys["public_key"]
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("\nGET request to %s\n" % endpoint)
        time.sleep(2)
        message = PMESClient._make_message()
        params = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"])
        }
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=params)
        try:
            return request.json()
        except:
            return request.text


    def get_balance(self):
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
            endpoint = input("Insert your url address ('/api/accounts/%s/balance' by default): " % keys["public_key"]) or "/api/accounts/%s/balance" % keys["public_key"]
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("GET request to /api/accounts/%s/%s" % (
                    keys["public_key"], "balance"))
        time.sleep(2)
        message = PMESClient._make_message()
        params = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
               keys["private_key"])
            }
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=params)
        print("\nGET request to %s\n" % url)
        try:
            return request.json()
        except:
            return request.text



    def get_data_from_blockchain(self):
        endpoint = input("Insert endpoint ('/api/blockchain/data') by default: ") or "/api/blockchain/data"
        try:
            with open("cookies.json") as cookiefile:
                cookies = json.load(cookiefile)
        except:
            cookies={}
        try:
            _hash = input("Insert hash (or i`ll get it from your cookies): ") or cookies["hash"]
        except:
            print("There are no data yet")
            return

        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("GET request to " + endpoint)
        time.sleep(2)
        message = PMESClient._make_message(account)
        params = {}
        if _hash:
            params["hash"] = _hash
        
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=params)
        try:
            with open("cookies.json") as cookiefile:
                cookie = json.load(cookiefile)
            with open("cookies.json", "w") as cookiefile:
                if _hash:
                    cookie["hash"] = _hash

                    if request.json()["cid"] and isinstance(request.json()["cid"], str) or isinstance(request.json()["cid"], int):
                        cookie["cid"] = request.json()["cid"]
                    else:
                        cookie["cid"] = None
                

                cookiefile.write(json.dumps(cookie))
            return request.json()
        except:
            return request.text


    def post_data_to_blockchain(self):
        endpoint = input("Insert your url ('/api/blockchain/data' by default): ") or "/api/blockchain/data"
        cus = input("Insert your data (required): ") or "My favorite data"
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("POST request to " + endpoint)
        time.sleep(2)
        message = PMESClient._make_message({"cus":cus})
        data = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"]),
            "cus": cus
        }
        
        url = "%s%s" % (self.host, endpoint)
        request = requests.post(url, data=data)
        try:
            with open("cookies.json") as cookiefile:
                cookie = json.load(cookiefile)
        except:
            cookie = {}

        _hash = None
        if "hash" in request.json().keys():
            _hash = request.json()["hash"]
        
        with open("cookies.json", "w") as cookiefile:
            cookie["hash"] = _hash
            cookie["cid"] = None
            cookiefile.write(json.dumps(cookie))

        if _hash:
            return "Your hash is: %s" % _hash
        else:
            return request.text




    def get_last_block_id(self):
        endpoint = input("Insert your url ('/api/blockchain/lastblockid' by default): ") or "/api/blockchain/lastblockid"
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url)
        try:
            return request.json()
        except:
            return request.text

        
    def get_owner(self):
        endpoint = input("Insert your url ('/api/blockchain/owner' by default): ") or "/api/blockchain/owner"
        try:
            with open("cookies.json") as cookiefile:
                cookies = json.load(cookiefile)
        except:
            cookies = {}
        while True:
            cid = input("Insert cid (or i`ll receive it from the cookies if the one does exist): ") or cookies.get("cid", None)
            if cid:
                break
            else:
                print("Insert cid. There is not any cid`s at cookies.")
                continue
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params={"cid": cid})
        try:
            return request.json()
        except:
            return request.text



    def change_owner(self):
        endpoint = input("Insert your url ('/api/blockchain/owner' by default): ") or "/api/blockchain/owner"
        try:
            with open("cookies.json") as cookiefile:
                cookies = json.load(cookiefile)
        except:
            cookies = {}
        cid = input("Insert cid (or i`ll receive it from the cookies): ") or cookies.get("cid", None)
        with open("generated.json") as genfile:
            genkeys = json.load(genfile)
            randkeys = random.choice(genkeys)
        with open("cookies.json") as cookiefile:
            cookies = json.load(cookiefile)
        new_owner_pubkey = input("Insert new owner public key (or the one`ll be generated by default): ") or randkeys["public_key"]
        access_string = input("Insert access string (or i`ll get it from cookies): ") or cookies.get("access_string", None)
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("POST request to " + endpoint)
        time.sleep(2)
        message = PMESClient._make_message({
                "cid":cid,
                "new_owner": new_owner_pubkey,
                "access_string": access_string
            })
        data = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"]),
            "cid":cid,
            "new_owner": new_owner_pubkey,
            "access_string": access_string
        }
        url = "%s%s" % (self.host, endpoint)
        request = requests.put(url, data=data)
        try:
            return request.json()
        except:
            return request.text


    def set_content_description(self):
        endpoint = input("Insert your url address ('/api/blockchain/description' by default): ") or "/api/blockchain/description"
        description = input("Insert description ('my description' by default)") or "my description"
        try:
            with open("cookies.json") as cookiefile:
                cookie = json.load(cookiefile)
        except:
            cookie = {}
        while True:
            cid = input("Insert cid (or i`ll receive it from the cookies if the one does exist): ") or cookie.get("cid", None)
            if cid:
                break
            else:
                print("Insert cid. There is not any cid`s at cookies.")
                continue
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)   
        message = PMESClient._make_message({
                "cid":cid,
                "descr": description,
            })
        data = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"]),
            "cid":cid,
            "descr": description
        }
        url = "%s%s" % (self.host, endpoint)
        request = requests.post(url, data=data)
        try:
            return request.json()
        except:
            return request.text



    def get_content_description(self):
        endpoint = input("Insert your url ('/api/blockchain/description') by default: ") or "/api/blockchain/description"
        try:
            with open("cookies.json") as cookiefile:
                cookie = json.load(cookiefile)
        except:
            cookie = {}
        while True:
            cid = input("Insert cid (or i`ll receive it from the cookies if the one does exist): ") or cookie.get("cid", None)
            if cid:
                break
            else:
                print("Insert cid. There is not any cid`s at cookies.")
                continue
        if not endpoint:
                endpoint = "/api/blockchain/description"
        params = {"cid":cid}
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=params)
        try:
            return request.json()
        except:
            return request.text


    def get_access_string(self):
        endpoint = input("Insert your url ('/api/blockchain/access_string' by default): ") or "/api/blockchain/access_string"
        try:
            with open("cookies.json") as cookiefile:
                cookies = json.load(cookiefile)
        except:
            cookies = {}
        while True:
            cid = input("Insert cid (or i`ll receive it from the cookies if the one does exist): ") or cookies.get("cid", None)
            if cid:
                break
            else:
                print("Insert cid. There is no any cid`s at cookies.")
                continue
        params = {"cid":cid}
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=params)
        try:
            return request.json()
        except:
            return request.text


    def sell_content(self):
        endpoint = input("Insert your url ('/api/blockchain/sale' by default): ") or "/api/blockchain/sale"
        try:
            with open("cookies.json") as cookiefile:
                cookie = json.load(cookiefile)
        except:
            cookie = {}
        while True:
            cid = input("Insert cid (or i`ll receive it from the cookies if the one does exist): ") or cookie.get("cid", None)
            if cid:
                break
            else:
                print("Insert cid. There is not any cid`s at cookies.")
                continue
        with open("generated.json") as genfile:
            genkeys = json.load(genfile)
            randkeys = random.choice(genkeys)
        buyer_pubkey = input("Insert buyer public key (or the one will be generated by default): ") or randkeys["public_key"]
        access_string = input("Insert access string: ") or cookie.get("access_string", None)
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("POST request to " + endpoint)
        time.sleep(2)
        message = PMESClient._make_message({
                "cid":cid,
                "buyer_pubkey": buyer_pubkey,
                "access_string": access_string
            })
        data = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"]),
            "cid":cid,
            "buyer_pubkey": buyer_pubkey,
            "access_string": access_string
        }
        url = "%s%s" % (self.host, endpoint)
        request = requests.post(url, data=data)
        try:
            return request.json()
        except:
            return request.text

    def setprice(self):
        endpoint = input("Insert your url address ('/api/blockchain/data/price' by default): ") or "/api/blockchain/data/price"
        cid = input("Insert cid: ") 
        price = input("Insert price: ")
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)   
        message = PMESClient._make_message({
                "cid":cid,
                "price": int(price),
            })
        data = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                            keys["private_key"]),
        }
        url = "%s%s" % (self.host, endpoint)
        request = requests.post(url, data=data)
        try:
            return request.json()
        except:
            return request.text

    def getprice(self):
        endpoint = input("Insert your url address ('/api/blockchain/data/price' by default): ") or "/api/blockchain/data/price"
        cid = input("Insert cid: ")
        data= {"cid":cid}
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=data)
        try:
            return request.json()
        except:
            return request.text


    def setnews(self):
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        url = "http://127.0.0.1:8001/api/storage"
        client = HTTPClient(url)


    def makeoffer(self):
        url = "http:127.0.0.1:8001/api/blo"


    def get_account_news(self):
        with open("keys.json") as keyfile:
            keys = json.load(keyfile)
        endpoint = input("Insert your account address ('/api/accounts/%s/news') by default: " % keys["public_key"]) or "/api/accounts/%s/news" % keys["public_key"]
        with open("account.json") as accountfile:
            account = json.load(accountfile)
        print("\nGET request to %s\n" % endpoint)
        time.sleep(2)
        message = PMESClient._make_message()
        params = {
            "public_key": keys["public_key"],
            "message": message,
            "signature": Bip32Keys.sign_message(message, 
                        keys["private_key"])
            }
        url = "%s%s" % (self.host, endpoint)
        request = requests.get(url, params=params)
        try:
            return request.json()
        except:
            return request.text