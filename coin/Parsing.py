from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from tornado_components.web import SignedHTTPClient
from settings import *


balance_server = balanceurl
qtum_server = "http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018")
coin_id = "QTUM"


class ClientBalance():
    """ Client for balance
    """
    def __init__(self, host=None):
        self.host = host if host else balance_server
        self.client = SignedHTTPClient(self.host)

    def get_balance(self, uids=None, coin_id=coin_id):
        # get balance for uid
        if uids:
            request = self.client.request(method_name="getbalance", address=uids, coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def inc_balance(self, uids=None, amount=.0, coin_id=coin_id):
        # increment for uid
        if uids:
            request = self.client.request(method_name="incbalance", address=uids, amount=amount, coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def dec_balance(self, uids=None, amount=.0, coin_id=coin_id):
        # decrement for uid
        if uids:
            request = self.client.request(method_name="decbalance", address=uids, amount=amount, coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def set_balance(self, uid, amount):
        return self.client.set_balance(uid, amount)


class ParsingBlock():
    """ Parsing all transaction in all blocks
    """
    def __init__(self, from_block=0, to_block=-1):
        self.from_block = from_block
        self.to_block = to_block
        self.qtum = AuthServiceProxy(qtum_server)
        self.client = ClientBalance()

    def block_hash_num(self, block=None):
        # get block hash
        try:
            if not block:
                block = self.from_block
            block_hash = self.qtum.getblockhash(block)
            return block_hash
        except:
            pass

    def get_transaction_in_block(self, block_hash=None):
        # get list transaction in block
        try:
            if not block_hash:
                block_hash = self.block_hash_num()
            block = self.qtum.getblock(block_hash)
            list_tx = block["tx"]
            return list_tx
        except:
            pass

    def get_raw_transaction(self, transaction_blocks=None):
        # get raw transaction
        try:
            if not transaction_blocks:
                transaction_blocks = self.get_transaction_in_block()
            transaction_list = []
            for transaction_block in transaction_blocks:
                try:
                    transaction_data = self.qtum.getrawtransaction(transaction_block)
                    transaction_list += [transaction_data]
                except JSONRPCException:
                    try:
                        transaction_data = self.qtum.gettransaction(transaction_block)
                        transaction_list += [transaction_data]
                    except JSONRPCException:
                        pass
            return transaction_list
        except:
            pass

    def transaction_in(self, vin):
        # parsing input
        try:
            for vin_i in vin:
                try:
                    txid = vin_i["txid"]
                    vout_num = vin_i["vout"]
                    encoded_datas = self.get_raw_transaction([txid])
                    for i in encoded_datas:
                        try:
                            transaction_data = self.qtum.decoderawtransaction(i)
                            vout_prev = transaction_data["vout"]
                            vout_prev_data = vout_prev[vout_num]
                            value_dec = vout_prev_data["value"]
                            script_pub_key = vout_prev_data["scriptPubKey"]
                            addresses = script_pub_key["addresses"]
                            value_int = int(value_dec*(10**8))
                        except:
                            pass
                    #pprint(vin_i)
                except:
                    pass
        except:
            pass

    def transaction_out(self, vout):
        # parsing output
        try:
            for vout_i in vout:
                try:
                    script_pub_key = vout_i["scriptPubKey"]
                    addresses = script_pub_key["addresses"]
                    value = vout_i["value"]
                    value_int = int(value*(10**8))
                    for adr in addresses:
                        data = self.client.get_balance(adr)
                        if type(data) == list:
                            update_data_1 = self.client.inc_balance(adr, value_int)
                except:
                    pass
        except:
            pass

    def decode_raw_transaction(self, encoded_datas=None):
        # decode raw transaction
        try:
            if not encoded_datas:
                encoded_datas = self.get_raw_transaction()
            for encoded_data in encoded_datas:
                transaction_data = self.qtum.decoderawtransaction(encoded_data)
                #vin = transaction_data["vin"]
                vout = transaction_data["vout"]
                #self.transaction_in(vin)
                self.transaction_out(vout)
        except:
            pass

    def get_block_count(self):
        # Get count documents in db
        return self.qtum.getblockcount()

    def show_db(self):
        # show db
        return self.db_wallet.show_db()
