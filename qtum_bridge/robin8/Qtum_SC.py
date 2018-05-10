from eth_abi import encode_abi, decode_abi
import codecs
from bitcoinrpc.authproxy import AuthServiceProxy
import time

contract_owner = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'
contract_owner_hex = 'fdc1ae05c161833cdf135863e332126e15d7568c'
contract_address = '4f9ab7a8f5a2238b4315978e14305ce8db856f34'


class Qtum_SC:
    send_params = {
        'amount': 0,
        'gasLimit': 250000,
        'gasPrice': '0.00000049',
        'sender': '',
    }

    def __init__(self, contract_address, func_hashes, qtum_rpc=None):
        self.reload_rpc(qtum_rpc)
        self.contract_address = contract_address
        self.func_hashes = func_hashes

        self.decode_hex = codecs.getdecoder("hex_codec")
        self.encode_hex = codecs.getencoder("hex_codec")

    def reload_rpc(self, qtum_rpc=None):
        if qtum_rpc is None:
            self.qtum_rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018"))
        elif type(qtum_rpc) is int:
            self.qtum_rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:%d" %
                                             ("qtumuser", "qtum2018", qtum_rpc))  # port specified
        else:
            self.qtum_rpc = qtum_rpc

    def set_send_params(self, send_params):
        self.send_params = {**self.send_params, **send_params}   #merge dicts

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

    def callcontract(self, func_name, input_types=None, input_values=None, output_types=None):
        data = self._pack_data(func_name, input_types, input_values)

        res = self.qtum_rpc.callcontract(self.contract_address, data)
        output = res['executionResult']['output']

        if output is not None and output_types is not None:
            return decode_abi(output_types, self.decode_hex(output)[0])
        else:
            return None

    def sendtocontract(self, func_name, input_types=None, input_values=None, output_types=None):
        data = self._pack_data(func_name, input_types, input_values)

        res = self.qtum_rpc.sendtocontract(self.contract_address, data,
                                           self.send_params['amount'],
                                           self.send_params['gasLimit'],
                                           self.send_params['gasPrice'],
                                           self.send_params['sender'])
        self.send_params['amount'] = 0  # prevent if someone occasionally forgets to zero amount

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
    abi = Qtum_SC.params_to_abi(types,
                                [555, 'Hello world'])
    decoded = Qtum_SC.abi_to_params('000000000000000000000000fd772dcff7a17307c2af99fdd2b0726de669c30600000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000870617373776f7264000000000000000000000000000000000000000000000000',
                                    ['address', 'uint32', 'string'])
    print('encoded: ', abi)
    print('decoded: ', decoded)

    func_hashes = {'add_num': 'cf0d6774', 'get_all': '880a3c86', 'get_num': '3e27a8e8', 'get_str': '70f9b8da'}

    test_sc = Qtum_SC(contract_address, func_hashes)
    res = test_sc.callcontract(func_name='get_num', output_types=['uint'])
    print('num: ', res)

    res = test_sc.callcontract(func_name='get_str', output_types=['string'])
    print('str: ', res)

    res = test_sc.callcontract(func_name='get_all', output_types=['uint', 'string'])
    print('all: ', res)

    arg = 100
    res = test_sc.callcontract(func_name='add_num', input_types=['uint'], input_values=[arg], output_types=['uint'])
    print('num + %d: %s' % (arg, res))