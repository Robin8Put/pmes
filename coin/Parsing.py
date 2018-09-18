import codecs
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from eth_abi import decode_abi
from qtum_utils.qtum import Qtum
from BalanceCli import ClientBalance, TablePars
from StorgCli import ClientStorge

import settings

qtum_server = "http://qtum:qtum123@190.2.148.12:50013"
coin_id = settings.QTUM
coin_id_put = "PUT"
sign_transfer = "a9059cbb"
address_smart_contract = ["4060e21ac01b5c5d2a3f01cecd7cbf820f50be95"]
mainnet_status = True


class ParsingBlock():
    """ Parsing all transaction in all blocks
    """

    def __init__(self, from_block=0, to_block=-1, db_host=None, db_name=None):
        self.from_block = from_block
        self.to_block = to_block
        self.coinid = coin_id
        self.qtum = AuthServiceProxy(qtum_server)
        self.client = ClientBalance(settings.balanceurl)
        self.db = TablePars(db_host, db_name)
        self.storge = ClientStorge(settings.storageurl)

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
            list_address = []
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
                            for adr in addresses:
                                list_address += [{adr: value_int}]
                        except:
                            pass
                except:
                    pass
            return list_address
        except:
            pass

    def transaction_out(self, vout, txid):
        # parsing output
        try:
            list_address = [False]
            for vout_i in vout:
                try:
                    script_pub_key = vout_i["scriptPubKey"]
                    types = script_pub_key["type"]
                    if types == "call" and self.coinid == coin_id:
                        asm = script_pub_key["asm"]
                        asm_split = asm.split()
                        gasLimit = asm_split[1]
                        gasPrice = asm_split[2]
                        asm_data = asm_split[3]
                        hex_address = asm_data[:8]
                        smart_contr_address = asm_split[4]
                        if smart_contr_address in address_smart_contract and hex_address == sign_transfer:
                            data = asm_data[8:]
                            signatures_list_type = ['address', 'uint']
                            try:
                                decode = self.abi_to_params(data, signatures_list_type)
                                new_decode = self.change_decode(signatures_list_type, decode)
                                address_token = new_decode[0]
                                value_int = new_decode[1]
                                address_token = Qtum.hex_to_qtum_address(address_token, mainnet=mainnet_status)
                                result = self.db.check_address(address=address_token, coinid=coin_id_put)
                                result_keys = result.keys()
                                if "address" in result_keys:
                                    update_data_1 = self.client.inc_balance(address_token, value_int, coin_id_put)
                                    self.storge.log_transaction(
                                        **{"coinid": coin_id_put,
                                           "blocknumber": self.from_block,
                                           "blockhash": self.block_hash_num(),
                                           "vin": [],
                                           "vout": [{address_token: value_int}],
                                           "txid": txid,
                                           "gasLimit": gasLimit,
                                           "gasPrice": gasPrice})
                            except Exception as e:
                                # print(e)
                                pass
                    addresses = script_pub_key["addresses"]
                    value = vout_i["value"]
                    value_int = int(value * (10 ** 8))
                    for adr in addresses:
                        data = self.db.check_address(adr, self.coinid)
                        result_keys = data.keys()
                        if "address" in result_keys:
                            update_data_1 = self.client.inc_balance(adr, value_int, coin_id)
                            list_address[0] = True
                        list_address += [{adr: value_int}]
                except:
                    pass
            return list_address
        except:
            pass

    def decode_raw_transaction(self, encoded_datas=None):
        # decode raw transaction
        try:
            if not encoded_datas:
                encoded_datas = self.get_raw_transaction()
            for encoded_data in encoded_datas:
                try:
                    transaction_data = self.qtum.decoderawtransaction(encoded_data)
                    # vin = transaction_data["vin"]
                    vout = transaction_data["vout"]
                    txid = transaction_data["txid"]
                    # self.transaction_in(vin)
                    vout_res = self.transaction_out(vout, txid)
                    if vout_res[0]:
                        vin_res = self.transaction_in(transaction_data["vin"])
                        self.storge.log_transaction(**{"coinid": self.coinid,
                                                       "blocknumber": self.from_block,
                                                       "blockhash": self.block_hash_num(),
                                                       "vin": vin_res,
                                                       "vout": vout_res[1:],
                                                       "txid": txid})
                except:
                    pass
        except:
            pass

    def change_decode(self, signatures_list_type, decode):
        decode = list(decode)
        if "address" in signatures_list_type:
            index_adr = signatures_list_type.index("address")
            decode_index_adr = decode[index_adr]
            new_adr = decode_index_adr[2:]
            decode[index_adr] = new_adr
        if "string" in signatures_list_type:
            index_str = signatures_list_type.index("string")
            decode_index_str = decode[index_str]
            new_str = decode_index_str.decode()
            decode[index_str] = new_str
        return decode

    def abi_to_params(self, abi, output_types):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        data = decode_hex(abi)[0]
        return decode_abi(output_types, data)

    def get_block_count(self):
        # Get count documents in db
        return self.qtum.getblockcount()
