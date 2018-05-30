import sys
import os
import logging
from jsonrpcclient.http_client import HTTPClient
from bitcoinrpc.authproxy import AuthServiceProxy
from Parsing import ParsingBlock, TableNew


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not BASE_DIR in sys.path:
    sys.path.append(BASE_DIR)

import settings

logging.basicConfig(level=logging.CRITICAL, filename="one_coin.log", format="%(message)s")
balance_server = settings.balanceurl
qtum_server = "http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018")
db_name = "pars"
collection = "data3"


class ClientBalance():
    """ Client for balance
    """
    def __init__(self, host=None):
        self.host = host if host else balance_server
        self.client = HTTPClient(self.host)

    def get_balance(self, uids=None, coin_id="QTUM"):
        # get balance for uid
        if uids:
            request = self.client.request(method_name="getbalance", address=uids)
            return request
        else:
            return {2: "Missing name uid"}

    def inc_balance(self, uids=None, amount=.0, coin_id="QTUM"):
        # increment for uid
        if uids:
            request = self.client.request(method_name="incbalance", address=uids, amount=amount)
            return request
        else:
            return {2: "Missing name uid"}

    def dec_balance(self, uids=None, amount=0, coin_id="QTUM"):
        # decrement for uid
        if uids:
            request = self.client.request(method_name="decbalance", address=uids, amount=amount)
            return request
        else:
            return {2: "Missing name uid"}

    def set_balance(self, uid, amount):
        return self.client.set_balance(uid, amount)


class ParsingBlockNew(ParsingBlock):
    """ Class for parsing blockchain and update servers wallet on balance
    """
    def __init__(self, from_block=0, db_name="pars", collection="data3", to_block=-1):
        super().__init__(from_block, to_block, db_name, collection)
        self.client = ClientBalance()
        self.from_block = from_block
        self.to_block = to_block
        self.qtum = AuthServiceProxy(qtum_server)
        self.db_wallet = TableNew(db_name, collection)

    def check(self, vout):
        # Update servers wallet on balance
        try:
            for vout_i in vout:
                try:
                    script_pub_key = vout_i["scriptPubKey"]
                    addresses = script_pub_key["addresses"]
                    value = vout_i["value"]
                    value_float = float(value)
                    value_int = int(value * (10 ** 8))
                    for adr in addresses:
                        data = self.client.get_balance(adr)
                        if data == {'error': 404}:
                            pass
                        else:
                            db_coin = self.db_wallet.insert_new(**{"adr": adr, "value": value_int})
                            update_data_1 = self.client.inc_balance(adr, value_float)
                except:
                    pass
        except:
            pass

    def decode_raw_transaction_vout(self, encoded_datas=None):
        # Decode blockchain transaction
        try:
            if not encoded_datas:
                encoded_datas = self.get_raw_transaction()
            for encoded_data in encoded_datas:
                transaction_data = self.qtum.decoderawtransaction(encoded_data)
                vin = transaction_data["vin"]
                vout = transaction_data["vout"]
                self.check(vout)
        except:
            pass

    def get_block_count(self):
        # Get count documents in db
        return self.qtum.getblockcount()
