from web3 import Web3, IPCProvider, HTTPProvider
from web3.middleware import geth_poa_middleware
import codecs
import time


class EthContractHandler:
    send_params = {
        'value': 0,
        'gasLimit': 250000,
        'gasPrice': 49000000000,
        'sender': ''
    }

    def __init__(self, eth_rpc, contract_address, abi):
        self.w3 = eth_rpc
        # self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        self.contract_address = contract_address
        self.abi = abi
        self.contract = self.w3.eth.contract(abi=abi, address=contract_address)

    @classmethod
    def from_http_provider(cls, http_provider, contract_address, abi):
        w3 = Web3(HTTPProvider(http_provider))
        w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        return cls(w3, contract_address, abi)

    @classmethod
    def from_connection(cls, connection, contract_address, abi):
        return cls(connection, contract_address, abi)

    @classmethod
    def from_ipc_path(cls, ipc_path, contract_address, abi):
        w3 = Web3(IPCProvider(ipc_path))
        w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        return cls(w3, contract_address, abi)

    def reload_http_provider(self, http_provider):
        self.w3 = Web3(HTTPProvider(http_provider))

    def reload_ipc_path(self, ipc_path):
        self.w3 = Web3(IPCProvider(ipc_path))

    # def get_nonce(self, private_key):
    #     account = self.w3.eth.account.privateKeyToAccount(self.send_params['private_key'])
    #     return self.w3.eth.getTransactionCount(account.address)

    # def update_nonce(self):
    #     self.send_params['nonce'] = self.get_nonce(self.send_params['private_key'])

    def set_send_params(self, send_params):
        self.send_params = {**self.send_params, **send_params}  # merge dicts
        # if 'private_key' in send_params:
        #     self.update_nonce()

    def get_contract(self):
        return self.contract

    def send_to_contract(self, fn):
        # account = self.w3.eth.account.privateKeyToAccount(self.send_params['private_key'])

        result = fn.transact({
            'from': self.send_params['sender'],
            'gas': self.send_params['gasLimit'],
            'gasPrice': self.send_params['gasPrice'],
            'value': self.send_params['value']})

        encode_hex = codecs.getencoder("hex_codec")
        result = encode_hex(result)[0].decode()

        return {'txid': result}


if __name__ == '__main__':
    ch = EthContractHandler.from_http_provider('https://rinkeby.infura.io/jPgsGcw3RjKP5MjlcJeg',
                                               '0xBc9df82727513A5F14315883A048324A1fAA0788',
                                               '[{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"description","type":"string"}],"name":"setDescription","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"cus","type":"string"}],"name":"getCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"publisherAddress","type":"address"},{"name":"accessLevel","type":"uint256"}],"name":"setAccessLevel","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"publishersMap","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"address"}],"name":"CidBuyerIdToOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"review","type":"string"}],"name":"addReview","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"CidToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"nextOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"},{"name":"buyerAccessString","type":"string"}],"name":"makeOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerPublicKey","type":"string"},{"name":"sellerAccessString","type":"string"}],"name":"sellContent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"offers","outputs":[{"name":"buyerAccessString","type":"string"},{"name":"sellerPublicKey","type":"string"},{"name":"sellerAccessString","type":"string"},{"name":"status","type":"uint8"},{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cus","type":"string"},{"name":"ownerId","type":"address"},{"name":"description","type":"string"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"name":"makeCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setReadPrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"uint256"}],"name":"BuyerIdToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"reviews","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"contents","outputs":[{"name":"cus","type":"string"},{"name":"description","type":"string"},{"name":"owner","type":"address"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerPublicKey","type":"string"},{"name":"sellerAccessString","type":"string"}],"name":"changeOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setWritePrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"nextCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"}],"name":"rejectOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]'
                                               )

    # ch.set_send_params({'private_key': '89b255e8b0ff38b033bb45202c2eb3d66b9044e5a4e5a290f1fdcded930abb35'})
    # print(ch.get_contract().functions.offers(1).call())
    #
    # print(ch.send_to_contract(ch.get_contract().functions.makeCid('Simplefdsr2fd22fd23423', '0xBc9df82727513A5F14315883A048324A1fAA0788', 'descr', 10000, 10000)))
    # print(ch.send_to_contract(ch.get_contract().functions.makeCid('Simple5fd333fdgss222', '0xBc9df82727513A5F14315883A048324A1fAA0788', 'descr5345435', 10000, 10000)))
    #
    # time.sleep(60)
    # #ch.reload_http_provider('https://rinkeby.infura.io/jPgsGcw3RjKP5MjlcJeg')
    # print(ch.send_to_contract(ch.get_contract().functions.makeCid('Simplefdsr222fdsdfd23fdfd423', '0xBc9df82727513A5F14315883A048324A1fAA0788', 'descr', 10000, 10000)))
    # print(ch.send_to_contract(ch.get_contract().functions.makeCid('Simple5fd333fdg2fdfd2fdf2', '0xBc9df82727513A5F14315883A048324A1fAA0788', 'descr5345435', 10000, 10000)))
