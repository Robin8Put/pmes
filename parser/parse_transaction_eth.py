import binascii
import codecs
from time import sleep
from eth_abi import decode_abi
from web3 import Web3, IPCProvider
from web3.middleware import geth_poa_middleware
from BalanceCli import ClientBalance
from StorgCli import ClientStorge
from settings_file import *
import settings


from_i = 2754475
coin_id = "ETH"


class SearchTransaction():
    def __init__(self, from_block=0, ipc_provider=ipc_provider):
        self.web3 = Web3(IPCProvider(ipc_provider))
        self.from_block = from_block
        self.client = self.conection_stor()
        self.balance = ClientBalance(settings.balanceurl)
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
        asm_data = vouts
        hex_address = asm_data[:8]
        data = asm_data[8:]
        signatures_list = signatures[hex_address]
        signatures_list_type = signatures_list[1]
        decode = self.abi_to_params(data, signatures_list_type)
        new_decode = self.change_decode(signatures_list_type, decode)
        data_write = [txid] + new_decode
        method = signatures_list[2]
        method_call = method(data_write)
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
            return transactions
        except Exception as e:
            pass

    def get_raw_transaction(self, transaction_blocks=None):
        # get raw transaction
        try:
            if not transaction_blocks:
                transaction_blocks = self.get_transaction_in_block()
            transaction_list = []
            for transaction_block in transaction_blocks:
                try:
                    transaction_data = dict(self.web3.eth.getTransaction(transaction_block))
                    transaction_block = binascii.hexlify(transaction_block).decode('utf-8')
                    transaction_data["tx_hash"] = transaction_block
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
                    to = encoded_data["to"]
                    if to == address_smart_contract:
                        txid = encoded_data["tx_hash"]
                        vout = encoded_data["input"][2:]
                        result = self.search_transaction(txid, vout)
                except:
                    pass
        except:
            pass

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
        result = self.client.mailed_confirm(cid=cid, buyer_address=address, offer_type=offer_type, price=price, coin_id=coin_id)

    def confirm_balance(self, data):
        tx_hash = data[0]
        cid = data[1]
        address = data[2]
        result = self.balance.confirm_balance(txid=tx_hash, cid=cid, buyer_address=address, coinid=coin_id)

    def update_review(self, data):
        txid = data[0]
        result = self.client.update_review(txid=txid, coin_id=coin_id)

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
    search_transaction = client.run(from_i, address_smart_contract_eth)
