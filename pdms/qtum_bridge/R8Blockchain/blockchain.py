from R8Blockchain.qtumblockchain import QtumBlockchain
from R8Blockchain.ethereumblockchain import EthereumBlockchain


class R8Blockchain:
    def __init__(self, handler):
        self.handler = handler

    @classmethod
    def init_qtum(cls, host, port, username=None, password=None):
        return cls(QtumBlockchain.from_host_port(host,port,username,password))

    @classmethod
    def init_ethereum(cls, host, port, username=None, password=None):
        return cls(EthereumBlockchain.from_host_port(host, port, username, password))

    def get_last_block_hash(self):
        return self.handler.get_last_block_hash()

    def get_second_last_block_hash(self):
        return self.handler.get_second_last_block_hash()

    def get_last_block_id(self):
        return self.handler.get_last_block_id()

    def get_second_last_block_id(self):
        return self.handler.get_second_last_block_id()

    def get_block_id(self, height):
        return self.handler.get_block_id(height)

    def get_block_hash(self, height):
        return self.handler.get_block_hash(height)

    def get_block_count(self):
        return self.handler.get_block_count()

    def get_unspent(self):
        return self.get_unspent()

    def get_accounts(self):
        return self.handler.get_accounts()

    def get_balance(self):
        return self.handler.get_balance()

    def from_hex_address(self, address):
        return self.handler.from_hex_address(address)

    def callcontract(self, contract_address, data):
        return self.handler.callcontract(contract_address, data)

    def sendtocontract(self, contract_address, data, sender, amount = 0, gasLimit = 250000, gasPrice = 0.00000049):
        return self.handler.sendtocontract(contract_address, data,
                                           amount,
                                           gasLimit,
                                           gasPrice,
                                           sender)
