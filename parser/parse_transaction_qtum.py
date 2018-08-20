import sys
import os
import codecs
from time import sleep
from eth_abi import  decode_abi
from jsonrpcclient.http_client import HTTPClient
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from BalanceCli import ClientBalance, TablePars
from StorgCli import ClientStorge
from settings_file import *
import settings



from qtum_utils.qtum import Qtum

from_i = 188780
coin_id = "QTUM"
db_host = "localhost"
db_name = "balance"


class SearchTransaction():
    def __init__(self, from_block=0, qtum_host=qtum_host_def, db_name=None, db_host=None):
        self.qtum = AuthServiceProxy(qtum_host)
        self.from_block = from_block
        self.client = self.conection_stor()
        self.balance = ClientBalance(settings.balanceurl)
        self.db = TablePars(db_host, db_name)
        self.coinid_put = "PUTTEST"

    def abi_to_params(self, abi, output_types):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        data = decode_hex(abi)[0]
        return decode_abi(output_types, data)

    def search_transaction(self, txid, address_smart_contract, vouts):
        signatures = {'8c3ce5d7': ['makeCid({0[0]}, {0[1]}, {0[2]}, {0[3]}, {0[4]})',
                                   ['string', 'address', 'string', 'uint256', 'uint256'],
                                   self.new_cid],

                      '65d72416': ['newOffer({0[0]}, {0[1]}, {0[2]}, {0[3]}, {0[4]})',
                                   ['uint256', 'address', 'uint256', 'uint256', 'string'],
                                   self.new_offer],

                      '715c084b': ['sellContent({0[0]}, {0[1]}, {0[2]})',
                                   ['uint256', 'address', 'string', 'string'],
                                   self.confirm_balance],

                      'bbfd5e53': ['changeOwner({0[0]}, {0[1]}, {0[2]})',
                                   ['uint256', 'address', 'string', 'string'],
                                   self.confirm_balance],

                      '41309af4': ["newReview({0[0]}, {0[1]}, {0[2]}, {0[3]})",
                                   ["uint256", "address", "string"],
                                   self.update_review],

                      'a9059cbb': ["",
                                   ['address', 'uint'],
                                   self.balance_put]

                      }
        list_data = []
        for vout in vouts:
            script_pub_key = vout["scriptPubKey"]
            types = script_pub_key["type"]
            if types == "call":
                asm = script_pub_key["asm"]
                asm_split = asm.split()
                asm_data = asm_split[3]
                smart_contr_address = asm_split[4]
                if smart_contr_address in address_smart_contract:
                    hex_address = asm_data[:8]
                    data = asm_data[8:]
                    signatures_list = signatures[hex_address]
                    signatures_list_type = signatures_list[1]
                    try:
                        decode = self.abi_to_params(data, signatures_list_type)
                        new_decode = self.change_decode(signatures_list_type, decode)
                        data_write = [txid] + new_decode
                        method = signatures_list[2]
                        method_call = method(data_write)
                        list_data += data
                    except Exception as e:
                        print(e)
        return list_data

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
                    transaction_data = [self.qtum.getrawtransaction(transaction_block)]
                    transaction_data += [transaction_block]
                    transaction_list += [transaction_data]
                except JSONRPCException:
                    try:
                        transaction_data = [self.qtum.gettransaction(transaction_block)]
                        transaction_data += [transaction_block]
                        transaction_list += [transaction_data]
                    except JSONRPCException:
                        pass
                        # print(transaction_block)
            return transaction_list
        except:
            pass

    def decode_raw_transaction(self, address_smart_contract, encoded_datas=None):
        # decode raw transaction
        try:
            if not encoded_datas:
                try:
                    encoded_datas = self.get_raw_transaction()
                except:
                    pass
            for encoded_data in encoded_datas:
                try:
                    transaction_data = self.qtum.decoderawtransaction(encoded_data[0])
                    txid = encoded_data[1]
                    vout = transaction_data["vout"]
                    result = self.search_transaction(txid, address_smart_contract, vout)
                except:
                    pass
        except:
            pass

    def balance_put(self, data):
        txid = data[0]
        address = data[1]
        address = Qtum.hex_to_qtum_address(address, mainnet=False)
        ammount = data[2]
        data = self.db.check_address(address, self.coinid_put)
        if data:
            update_data_1 = self.balance.inc_balance(address, ammount, self.coinid_put)

    def new_cid(self, data):
        tx_hash = data[0]
        cid = data[1]
        result = self.client.update_users_content(txid=tx_hash, coin_id=coin_id)

    def new_offer(self, data):
        txid = data[0]
        cid = data[1]
        address = data[2]
        offer_type = data[3]
        price = data[4]
        self.client.update_offer(txid, coin_id=coin_id)
        mail = self.client.mailed_confirm(cid=cid, buyer_address=address, offer_type=offer_type, price=price, coin_id=coin_id)

    def confirm_balance(self, data):
        tx_hash = data[0]
        cid = data[1]
        address = data[2]
        result = self.balance.confirm_balance(txid=tx_hash, cid=cid, buyer_address=address, coinid=coin_id)

    def update_review(self, data):
        txid = data[0]
        self.client.update_review(txid, coin_id=coin_id)

    def conection_stor(self):
        while True:
            try:
                cli = ClientStorge(storghost)
                return cli
            except:
                sleep(1)


def run(from_i, address_smart_contract, db_name, db_host):
    while True:
        pars = SearchTransaction(from_i, db_name=db_name, db_host=db_host)
        getlastblock = pars.qtum.getblockcount()
        if getlastblock >= from_i:
            result = pars.decode_raw_transaction(address_smart_contract)
            print(from_i)
            from_i += 1
        else:
            sleep(1)


if __name__ == "__main__":
    run(from_i, address_smart_contract_qtum, db_name, db_host)
