import binascii
from web3 import Web3, IPCProvider
from web3.middleware import geth_poa_middleware
from time import sleep
from binascii import unhexlify
from pprint import pprint
import pymongo
from BalanceCli import ClientBalance, TablePars
import settings
import os

balance_host = settings.balancehost
home = os.path.expanduser("~")
eth_host = "{}/.ethereum/rinkeby/geth.ipc".format(home)
coin_id_eth = "ETH"
from_i_eth = 2703317
db_host = "localhost"
db_name = "PDMS_balance"


class Parsing():
    """
    Parsing all transaction in all blocks
    """
    def __init__(self, from_block=0, host=None, coin_id=None, db_host=None, db_name=None, balance_host=None):
        self.from_block = from_block
        self.connect = Web3(IPCProvider(host))
        self.coin_id = coin_id
        self.connect.middleware_stack.inject(geth_poa_middleware, layer=0)
        self.db = TablePars(db_host, db_name)
        self.balance = ClientBalance(balance_host)

    def get_transaction_in_block(self, block=None):
        # get list transaction in block
        try:
            if not block:
                block = self.from_block
            block = self.connect.eth.getBlock(block)
            transactions = block.transactions
            return transactions
        except Exception as e:
            info = "Invalid get_transaction_in_block: {e}".format(e=e)
            # print(info)

    def get_raw_transaction(self, transaction_blocks=None):
        # get raw transaction
        try:
            if not transaction_blocks:
                transaction_blocks = self.get_transaction_in_block()
            transaction_list = []
            for transaction_block in transaction_blocks:
                try:
                    transaction_data = self.connect.eth.getTransaction(transaction_block)
                    transaction_list += [transaction_data]
                except Exception as e:
                    info = "Invalid get_raw_transaction: {e}\ntransaction_block: {transaction_block}".format(e=e, transaction_block=transaction_block)
                    # print(info)
            return transaction_list
        except Exception as e:
            info = "Invalid get_raw_transaction: {e}".format(e=e)
            # print(info)

    def decode_raw_transaction(self,  encoded_datas=None):
        # decode raw transaction
        try:
            if not encoded_datas:
                try:
                    encoded_datas = self.get_raw_transaction()
                except:
                    pass
            for encoded_data in encoded_datas:
                try:
                    txid_hex = encoded_data["hash"]
                    txid = txid_hex.hex()
                    from_a = encoded_data["from"]
                    to = encoded_data["to"]
                    value = int(encoded_data["value"]*10**(-10))  # value == 10**18   // **(-10)
                    to_a = to.lower()
                    result = self.db.check_address(address=to_a, coinid=self.coin_id)
                    if result:
                        self.vout_logic(to, value)
                except Exception as e:
                    pass
        except:
            pass

    def vout_logic(self, to, value):
        try:
            result = self.balance.inc_balance(address=to, amount=value, coinid=self.coin_id)
        except:
            pass

    def get_block_count(self):
        # Get count block
        return self.connect.eth.blockNumber


def start(from_block, host, coin_id):
    while True:
        try:
            pars = Parsing(from_block, host, coin_id, db_host, db_name, balance_host=balance_host)
            best_block = pars.get_block_count()
            if best_block >= from_block:
                pars.decode_raw_transaction()
                print(from_block)
                from_block += 1
            else:
                sleep(1)
        except Exception as e:
            info = "Error with connection"
            print(info, e)
            sleep(10)


if __name__ == "__main__":
    start(from_i_eth, eth_host, coin_id_eth)
