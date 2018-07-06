from R8Blockchain.qtumblockchain import QtumBlockchain
from R8Blockchain.ethereumblockchain import EthereumBlockchain


class R8Blockchain:
    def __init__(self, handler):
        self.handler = handler

    @classmethod
    def init_qtum_http(cls, http_provider):
        return cls(QtumBlockchain.from_http_provider(http_provider))

    @classmethod
    def init_ethereum_ipc(cls, ipc_path):
        return cls(EthereumBlockchain.from_ipc_path(ipc_path))

    @classmethod
    def init_ethereum_http(cls, http_provider):
        return cls(EthereumBlockchain.from_http_provider(http_provider))

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

