from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from models import Table


class TableNew(Table):
    """ Add new specific db methods
    """
    def update_inc(self, id=None, name=None, value=1):
        if not id:
            return {3: "Missing id"}
        elif self.email.find_one({"id": id}):
            name_up = self.email.find_one_and_update({"id": id}, {"$inc": {name: value}})
            return {0: "Success"}
        return {5: "Error"}

    def insert_new(self, **data):
        try:
            self.email.insert_one(data)
            return {0: "Success"}
        except:
            return {1: "Failed"}


class ParsingBlock():
    """ Parsing all transaction in all blocks
    """
    def __init__(self, from_block=0, to_block=-1, db_name="pars", collection="wallet7"):
        self.from_block = from_block
        self.to_block = to_block
        self.qtum = AuthServiceProxy("http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018"))
        self.db_wallet = TableNew(db_name, collection)

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
                except JSONRPCException:
                    try:
                        send_data = self.qtum.sendrawtransaction(transaction_block)
                    except JSONRPCException:
                        pass
                else:
                    transaction_list += [transaction_data]
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
                        transaction_data = self.qtum.decoderawtransaction(i)
                        vout_prev = transaction_data["vout"]
                        vout_prev_data = vout_prev[vout_num]
                        value_dec = vout_prev_data["value"]
                        script_pub_key = vout_prev_data["scriptPubKey"]
                        addresses = script_pub_key["addresses"]
                        value_int = int(value_dec*(10**8))
                        for address in addresses:
                            news = self.db_wallet.update_inc(address, "value", -value_int)
                except KeyError:
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
                        if not self.db_wallet.find({'id': adr}):
                            data = self.db_wallet.insert(adr, **{"value": 0})
                        news = self.db_wallet.update_inc(adr, "value", value_int)
                except KeyError:
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
                vin = transaction_data["vin"]
                vout = transaction_data["vout"]
                self.transaction_out(vout)
                self.transaction_in(vin)
        except:
            pass

    def show_db(self):
        # show db
        return self.db_wallet.show_db()
