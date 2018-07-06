from time import sleep
from pprint import pprint
import codecs
from eth_abi import encode_abi, decode_abi
from jsonrpcclient.http_client import HTTPClient
from tornado_components.web import SignedHTTPClient
from web3 import Web3, IPCProvider, HTTPProvider
import os
import binascii
from web3.middleware import geth_poa_middleware

address_smart_contract = "0xBc9df82727513A5F14315883A048324A1fAA0788"
# txid = "d67284450fa37b92aad9f902b262dbc078a53fc235be6faab9d989c4dcda36f3"
# qtum_host_def = "http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018")
from_i = 2586585
coin_id = "ETH"
storghost = "http://192.168.1.199:8001/api/storage"
balance_server = "http://192.168.1.199:8004/api/balance"
home = os.path.expanduser("~")
ipc_provider = "{}/.ethereum/rinkeby/geth.ipc".format(home)


class ClientBalance():
    """ Client for balance
    """

    def __init__(self, host=None):
        self.host = host if host else balance_server
        self.client = SignedHTTPClient(self.host)

    def get_balance(self, uids=None, coin_id=coin_id):
        # get balance for uid
        if uids:
            request = self.client.request(method_name="getbalance",
                                          address=uids,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def inc_balance(self, uids=None, amount=.0, coin_id=coin_id):
        # increment for uid
        if uids:
            request = self.client.request(method_name="incbalance",
                                          address=uids,
                                          amount=amount,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def dec_balance(self, uids=None, amount=.0, coin_id=coin_id):
        # decrement for uid
        if uids:
            request = self.client.request(method_name="decbalance",
                                          address=uids,
                                          amount=amount,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def set_balance(self, uid, amount):
        return self.client.set_balance(uid, amount)

    def confirm_balance(self, txid=None, buyer_address=None, cid=None, coin_id=coin_id):
        if txid and buyer_address and cid:
            request = self.client.request(method_name="confirmbalance",
                                          txid=txid,
                                          cid=cid,
                                          buyer_address=buyer_address,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}



class ClientStorge():
    def __init__(self, sotrg_host=None):
        self.history_host = sotrg_host if sotrg_host else storghost
        self.client = HTTPClient(self.history_host)

    def insert_offer(self, cid=None, buyer_addr=None, price=None, coinid=coin_id):
        if cid and buyer_addr and price:
            try:
                request = self.client.request(method_name="insertoffer",
                                              cid=cid,
                                              buyer_address=buyer_addr,
                                              price=price,
                                              coinid=coinid)
                return request
            except:
                print("Erorr from insertoffer")
        else:
            return {2: "Missing parameter"}

    def get_offer(self, cid=None, buyer_addr=None, coinid=coin_id):
        if cid and buyer_addr:
            try:
                request = self.client.request(method_name="getoffer",
                                              cid=cid,
                                              buyer_address=buyer_addr,
                                              coinid=coinid)
                return request
            except:
                print("Erorr from getoffer")
        else:
            return {2: "Missing parameter"}

    def update_offer(self, txid=None, coinid=coin_id):
        if txid:
            try:
                request = self.client.request(method_name="updateoffer",
                                              txid=txid,
                                              coinid=coinid)
                return request
            except Exception as e:
                print("Erorr from updateoffer", e)
        else:
            return {2: "Missing parameter"}

    def mailed_confirm(self, cid=None, buyer_address=None, offer_type=None, price=None, coinid=coin_id):
        if cid and buyer_address and price:
            try:
                request = self.client.request(method_name="mailedconfirm",
                                              cid=cid,
                                              buyer_address=buyer_address,
                                              price=price,
                                              offer_type=offer_type,
                                              coinid=coinid)
                return request
            except Exception as e:
                return e
        else:
            return {2: "Missing parameter"}

    def update_users_content(self, txid=None, coinid=coin_id):
        if txid:
            try:
                request = self.client.request(method_name="updateuserscontent",
                                              txid=txid,
                                              coinid=coinid)
                return request
            except:
                print("Erorr from updateuserscontent")
        else:
            return {2: "Missing parameter"}

    def update_review(self, txid=None, coinid=coin_id):
        if txid:
            try:
                request = self.client.request(method_name="updatereview",
                                              txid=txid,
                                              coinid=coinid)
                return request
            except:
                print("Erorr from updatereview")
        else:
            return {2: "Missing parameter"}


class SearchTransaction():
    def __init__(self, from_block=0, ipc_provider=ipc_provider):
        self.web3 = Web3(IPCProvider(ipc_provider))
        self.from_block = from_block
        self.client = self.conection_stor()
        self.balance = ClientBalance(balance_server)
        #self.web3.personal.unlockAccount('0xe630f8dd65f9be1ef2588da43c83b697a270d12e', "eth2018")
        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)

    def abi_to_params(self, abi, output_types):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        data = decode_hex(abi)[0]
        return decode_abi(output_types, data)

    def search_transaction(self, txid, vouts):
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
                      }
        list_data = []
        # hex_block = self.qtum.getrawtransaction(txid)
        # decode_block = self.qtum.decoderawtransaction(hex_block)
        # pprint(decode_block)
        # vouts = decode_block["vout"]
        asm_data = vouts
        hex_address = asm_data[:8]
        data = asm_data[8:]
        signatures_list = signatures[hex_address]
        signatures_list_type = signatures_list[1]
        # signatures_list_text = signatures_list[0]
        # print(data, signatures_list_type)
        decode = self.abi_to_params(data, signatures_list_type)
        new_decode = self.change_decode(signatures_list_type, decode)
        data_write = [txid] + new_decode
        # print(data_write)
        method = signatures_list[2]
        method_call = method(data_write)
        # print(method_call)
        # print(map(signatures_list[2], data))
        # print(data)
        # decode_string = signatures_list_text.format(new_decode)
        # print(decode_string)
        list_data += [data]
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

    def get_transaction_in_block(self, block=None):
        # get list transaction in block
        try:
            if not block:
                block = self.from_block
            block = self.web3.eth.getBlock(block)
            transactions = block.transactions
            # print(transactions)
            # list_tx = block["tx"]
            return transactions
        except Exception as e:
            pass

    def get_raw_transaction(self, transaction_blocks=None):
        # get raw transaction
        try:
            if not transaction_blocks:
                transaction_blocks = self.get_transaction_in_block()
                # print(transaction_blocks)
            transaction_list = []
            for transaction_block in transaction_blocks:
                try:
                    transaction_data = dict(self.web3.eth.getTransaction(transaction_block))
                    transaction_block = binascii.hexlify(transaction_block).decode('utf-8')
                    transaction_data["tx_hash"] = transaction_block
                    # print(transaction_data)
                    transaction_list += [transaction_data]
                except Exception as e:
                    print(e)
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
                    # encoded_data = encoded_datas[2]
                    # encoded_data = encoded_data[0]
                    # print(encoded_data)
                    # transaction_data = self.qtum.decoderawtransaction(encoded_data)
                    # pprint(encoded_data)
                    # print(transaction_data)
                    # vin = transaction_data["vin"]
                    # print(vin)
                    # print(encoded_data)
                    to = encoded_data["to"]
                    if to == address_smart_contract:
                        txid = encoded_data["tx_hash"]
                        vout = encoded_data["input"][2:]
                        result = self.search_transaction(txid, vout)
                        # print(result)
                except:
                    pass
        except:
            pass

    def new_cid(self, data):
        tx_hash = data[0]
        cid = data[1]
        # print(tx_hash)
        # txid = binascii.hexlify(tx_hash).decode('utf-8')
        # print(tx_hash)
        result = self.client.update_users_content(txid=tx_hash)

    def new_offer(self, data):
        txid = data[0]
        cid = data[1]
        address = data[2]
        offer_type = data[3]
        price = data[4]
        self.client.update_offer(txid)
        result = self.client.mailed_confirm(cid=cid, buyer_address=address, offer_type=offer_type, price=price)

    def confirm_balance(self, data):
        tx_hash = data[0]
        cid = data[1]
        address = data[2]
        result = self.balance.confirm_balance(txid=tx_hash, cid=cid, buyer_address=address)

    def update_review(self, data):
        txid = data[0]
        self.client.update_review(txid)

    def conection_stor(self):
        while True:
            try:
                cli = ClientStorge(storghost)
                return cli
            except:
                sleep(1)

    def run(self, from_i, address_smart_contract):
        while True:
            getlastblock = self.web3.eth.blockNumber
            if getlastblock >= from_i:
                pars = SearchTransaction(from_i)
                result = pars.decode_raw_transaction(address_smart_contract)
                print(from_i)
                from_i += 1
            else:
                sleep(1)


if __name__ == "__main__":
    client = SearchTransaction()
    search_transaction = client.run(from_i, address_smart_contract)
    #print(search_transaction)

    # bal = ClientBalance()
    # print(bal.confirm_balance("99bd6b923fe517c5dde0096c32b64cc6178210993ff36858eb28fe3fa49f60d3", "e7c5aac6416440cafb65a8f92e8bb495bb26e58a", 14))
