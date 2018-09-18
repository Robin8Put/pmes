from eth_abi import encode_abi, decode_abi
import codecs
from bitcoinrpc.authproxy import AuthServiceProxy
from contract_handlers.utils import abi_to_func_hashes

contract_owner = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'
contract_owner_hex = 'fdc1ae05c161833cdf135863e332126e15d7568c'
contract_address = '4f9ab7a8f5a2238b4315978e14305ce8db856f34'


class QtumContractHandler:
    send_params = {
        'value': 0,
        'gasLimit': 500000,
        'gasPrice': 490000000000,
        'sender': '',
    }

    def __init__(self, qtum_rpc, contract_address, abi):
        self.contract_address = contract_address
        self.func_hashes = abi_to_func_hashes(abi)
        self.qtum_rpc = qtum_rpc

        self.decode_hex = codecs.getdecoder("hex_codec")
        self.encode_hex = codecs.getencoder("hex_codec")

    @classmethod
    def from_http_provider(cls, http_provider, contract_address, abi):
        return cls(AuthServiceProxy(http_provider), contract_address, abi)

    @classmethod
    def from_connection(cls, connection, contract_address, abi):
        return cls(connection, contract_address, abi)

    def reload_http_provider(self, http_provider):
        self.qtum_rpc = AuthServiceProxy(http_provider)

    def set_provider(self, provider):
        self.qtum_rpc = provider

    def set_send_params(self, send_params):
        self.send_params = {**self.send_params, **send_params}  # merge dicts

    def get_contract_address(self):
        return self.contract_address

    def get_func_hashes(self):
        return self.func_hashes

    def get_rpc(self):
        return self.qtum_rpc

    def _pack_data(self, func_name, input_types, input_values):
        try:
            data = self.func_hashes[func_name]
        except:
            raise Exception('Unknown method')
        if input_types is not None:
            data += self.encode_hex(encode_abi(input_types, input_values))[0].decode()
        return data

    def call_contract(self, func_name, input_types=None, input_values=None, output_types=None):
        data = self._pack_data(func_name, input_types, input_values)

        res = self.qtum_rpc.callcontract(self.contract_address, data)
        output = res['executionResult']['output']

        if output is not None and output_types is not None:
            return decode_abi(output_types, self.decode_hex(output)[0])
        else:
            return None

    def send_to_contract(self, func_name, input_types=None, input_values=None, output_types=None):
        data = self._pack_data(func_name, input_types, input_values)

        res = self.qtum_rpc.sendtocontract(self.contract_address, data,
                                           self.send_params['value'],
                                           self.send_params['gasLimit'],
                                           str(self.send_params['gasPrice'] / 10 ** 18),
                                           self.send_params['sender'])
        print('hell')
        self.send_params['value'] = 0  # prevent if someone occasionally forgets to zero amount

        return res  # currently qtum daemon doesn't return execution output

    def deploy_contract(self, contract_code):

        res = self.qtum_rpc.createcontract(contract_code,
                                           self.send_params['gasLimit'],
                                           str(self.send_params['gasPrice'] / 10 ** 18),
                                           self.send_params['sender'])

        return res  # currently qtum daemon doesn't return execution output

    @staticmethod
    def params_to_abi(input_types, input_values):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")

        return encode_hex(encode_abi(input_types, input_values))[0].decode()

    @staticmethod
    def abi_to_params(abi, output_types):
        decode_hex = codecs.getdecoder("hex_codec")
        encode_hex = codecs.getencoder("hex_codec")

        data = decode_hex(abi)[0]
        return decode_abi(output_types, data)


if __name__ == '__main__':
    types = ['uint', 'string']
    abi = QtumContractHandler.params_to_abi(types,
                                            [555, 'Hello world'])
    decoded = QtumContractHandler.abi_to_params(
        '000000000000000000000000fd772dcff7a17307c2af99fdd2b0726de669c30600000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000870617373776f7264000000000000000000000000000000000000000000000000',
        ['address', 'uint32', 'string'])
    print('encoded: ', abi)
    print('decoded: ', decoded)

    func_hashes = {'add_num': 'cf0d6774', 'get_all': '880a3c86', 'get_num': '3e27a8e8', 'get_str': '70f9b8da'}

    test_sc = QtumContractHandler(contract_address, func_hashes)
    res = test_sc.call_contract(func_name='get_num', output_types=['uint'])
    print('num: ', res)

    res = test_sc.call_contract(func_name='get_str', output_types=['string'])
    print('str: ', res)

    res = test_sc.call_contract(func_name='get_all', output_types=['uint', 'string'])
    print('all: ', res)

    arg = 100
    res = test_sc.call_contract(func_name='add_num', input_types=['uint'], input_values=[arg], output_types=['uint'])
    print('num + %d: %s' % (arg, res))
