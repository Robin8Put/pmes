from web3 import Web3, IPCProvider, HTTPProvider
from web3.middleware import geth_poa_middleware
import codecs

class EthContractHandler:
    send_params = {
        'value': 0,
        'gasLimit': 250000,
        'gasPrice': 49000000000,
        'private_key': '',
    }

    def __init__(self, eth_rpc, contract_address, abi):
        self.w3 = eth_rpc
        self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        self.contract_address = contract_address
        self.abi = abi
        self.contract = self.w3.eth.contract(abi=abi, address=contract_address)

    @classmethod
    def from_http_provider(cls, http_provider, contract_address, abi):
        return cls(Web3(HTTPProvider(http_provider)), contract_address, abi)

    @classmethod
    def from_ipc_path(cls, ipc_path, contract_address, abi):
        return cls(Web3(IPCProvider(ipc_path)), contract_address, abi)

    def set_send_params(self, send_params):
        self.send_params = {**self.send_params, **send_params}   #merge dicts

    def get_contract(self):
        return self.contract

    def send_to_contract(self, fn):
        account = self.w3.eth.account.privateKeyToAccount(self.send_params['private_key'])

        construct_txn = fn.buildTransaction({
            'from': account.address,
            'nonce': self.w3.eth.getTransactionCount(account.address),
            'gas': self.send_params['gasLimit'],
            'gasPrice': self.send_params['gasPrice'],
            'value': self.send_params['value']})

        signed = account.signTransaction(construct_txn)

        result = self.w3.eth.sendRawTransaction(signed.rawTransaction)
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")
        result = encode_hex(result)[0].decode()
        return {'txid': result}


if __name__ == '__main__':
    with open('robin8.abi') as f:
        abi = f.read()
    ch = EthContractHandler.from_http_provider('http://qtumuser:qtum2018@127.0.0.1:8333', '363d33ed942bd543b073101fa6e5ee00aa67cbad190cce8e', abi)
    ch.set_send_params({'private_key': 'f66a89b636ed5738b3abda384f1b91d6b314825307d8bb32411d1af7d3006341'})
    print(ch.get_contract().functions.getCUS(1))

    # ch.send_to_contract(ch.get_contract().functions.makeCID('Simple', '0x8EcBec1639a0B4313E493158b0a1169526D836b6', 'descr', 10000, 10000),
    #                   '89b255e8b0ff38b033bb45202c2eb3d66b9044e5a4e5a290f1fdcded930abb35')
