from web3 import Web3, IPCProvider, HTTPProvider
from web3.middleware import geth_poa_middleware
from R8Blockchain.blockchain_handler import BlockchainHandler
from hashlib import sha256
import codecs
from web3.contract import ConciseContract


class EthereumBlockchain(BlockchainHandler):
    def __init__(self, eth_rpc):
        self.w3 = eth_rpc
        self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        self.decode_hex = codecs.getdecoder("hex_codec")
        self.encode_hex = codecs.getencoder("hex_codec")

    @classmethod
    def from_ipc_path(cls, ipc_path):
        return cls(Web3(IPCProvider(ipc_path)))

    @classmethod
    def from_http_provider(cls, http_provider):
        return cls(Web3(HTTPProvider(http_provider)))

    def reload_http_provider(self, http_provider):
        self.w3 = Web3(HTTPProvider(http_provider))

    def reload_ipc_path(self, ipc_path):
        self.w3 = Web3(IPCProvider(ipc_path))

    def get_last_block_hash(self):
        return self.encode_hex(self.w3.eth.getBlock('latest').hash)[0].decode()

    def get_second_last_block_hash(self):
        return self.encode_hex(self.w3.eth.getBlock(self.get_block_count()-1).hash)[0].decode()

    def get_last_block_id(self):
        return self.get_block_id(self.get_block_count())

    def get_second_last_block_id(self):
        return self.get_block_id(self.get_block_count()-1)

    def get_block_id(self, height):
        block_hash = self.get_block_hash(height)

        l = sha256(self.decode_hex(block_hash)[0]).hexdigest()
        r = hex(height)

        return l[0:10] + r[2:].rjust(10, '0')

    def get_block_hash(self, height):
        return self.encode_hex(self.w3.eth.getBlock(height).hash)[0].decode()

    def get_block_count(self):
        return self.w3.eth.blockNumber

    def get_unspent(self):
        accounts = self.w3.personal.listAccounts

        return {acc: self.w3.eth.getBalance(acc) for acc in accounts}

    def get_accounts(self):
        return self.w3.personal.listAccounts

    def get_balance(self):
        res = 0
        for account in self.get_accounts():
            res += self.w3.eth.getBalance(account)
        return res

    def from_hex_address(self, address):
        return address



if __name__ == '__main__':
    eth_blockchain = EthereumBlockchain.from_ipc_path(ipc_path='/home/artem/.ethereum/rinkeby/geth.ipc')
    res = eth_blockchain.get_last_block_hash()
    print(eth_blockchain.get_block_count())
    res = eth_blockchain.get_block_hash(1200)
    print(res)
    print(eth_blockchain.get_balance())
    print(eth_blockchain.get_unspent())

