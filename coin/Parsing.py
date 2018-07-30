import os
import sys
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from BalanceCli import ClientBalance, TablePars

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tornado_components.web import SignedHTTPClient

balance_server = "http://localhost:8004/api/balance"
qtum_server = "http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018")
coin_id = "QTUMTEST"


class ParsingBlock():
    """ Parsing all transaction in all blocks
    """

    def __init__(self, from_block=0, to_block=-1, db_host=None, db_name=None):
        self.from_block = from_block
        self.to_block = to_block
        self.coinid = coin_id
        self.qtum = AuthServiceProxy(qtum_server)
        self.client = ClientBalance(balance_server)
        self.db = TablePars(db_host, db_name)

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
                            value_int = int(value_dec * (10 ** 8))
                        except:
                            pass
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
                    value_int = int(value * (10 ** 8))
                    for adr in addresses:
                        data = self.db.check_address(adr, self.coinid)
                        if data:
                            update_data_1 = self.client.inc_balance(adr, value_int, coin_id)
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
                # vin = transaction_data["vin"]
                vout = transaction_data["vout"]
                # self.transaction_in(vin)
                self.transaction_out(vout)
        except:
            pass

    def get_block_count(self):
        # Get count documents in db
        return self.qtum.getblockcount()
