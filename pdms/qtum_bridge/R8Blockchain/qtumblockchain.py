from bitcoinrpc.authproxy import AuthServiceProxy
from hashlib import sha256
from R8Blockchain.blockchain_handler import BlockchainHandler
import codecs
import logging


class QtumBlockchain(BlockchainHandler):
    def __init__(self, qtum_rpc):
        self.qtum_rpc = qtum_rpc

        self.decode_hex = codecs.getdecoder("hex_codec")
        self.encode_hex = codecs.getencoder("hex_codec")

    @classmethod
    def from_host_port(cls, host='127.0.0.1', port=8333, username=None, password=None):
        if username is None or password is None or username == '' or password == '':
            return cls(AuthServiceProxy("http://%s:%d" % (host, port)))
        else:
            logging.debug("http://%s:%s@%s:%d" % (username, password, host, port))
            qtum_rpc = AuthServiceProxy("http://%s:%s@%s:%d" % (username, password, host, port))
            logging.debug(qtum_rpc.getbestblockhash())
            return cls(qtum_rpc)

    def get_block_count(self):
        return self.qtum_rpc.getblockcount()

    def get_balance(self):
        return self.qtum_rpc.getbalance()

    def get_last_block_hash(self):
        return self.qtum_rpc.getbestblockhash()

    def get_second_last_block_hash(self):
        return self.get_block_hash(self.get_block_count()-1)

    def get_block_hash(self, height):
        return self.qtum_rpc.getblockhash(height)

    def get_block_id(self, height):
        block_hash = self.get_block_hash(height)

        l = sha256(self.decode_hex(block_hash)[0]).hexdigest()
        r = hex(height)

        return l[0:10] + r[2:].rjust(10, '0')

    def get_last_block_id(self):
        last_block_height = self.get_block_count()

        return self.get_block_id(last_block_height)

    def get_second_last_block_id(self):
        last_block_height = self.get_block_count() - 1

        return self.get_block_id(last_block_height)

    def get_accounts(self):
        unspent = self.qtum_rpc.listunspent()
        res = [tx['address'] for tx in unspent]

        return res

    def get_unspent(self):
        unspent = self.qtum_rpc.listunspent()
        res = {tx['address']: tx['amount'] for tx in unspent}

        return res

    def from_hex_address(self, address):
        return self.qtum_rpc.fromhexaddress(address)

    def callcontract(self, contract_address, data):
        return self.qtum_rpc.callcontract(contract_address, data)

    def sendtocontract(self, contract_address, data, sender, amount = 0, gasLimit = 250000, gasPrice = 0.00000049):
        res = self.qtum_rpc.sendtocontract(contract_address, data,
                                           amount,
                                           gasLimit,
                                           gasPrice,
                                           sender)
        return res


