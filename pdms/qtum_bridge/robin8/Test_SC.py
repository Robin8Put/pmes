from robin8.Qtum_SC import Qtum_SC
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time

contract_owner = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'
contract_owner_hex = 'fdc1ae05c161833cdf135863e332126e15d7568c'
contract_address = '4f9ab7a8f5a2238b4315978e14305ce8db856f34'


class Test_SC(Qtum_SC):
    def __init__(self, contract_address, qtum_rpc=None):
        func_hashes = {
            'add_num': "cf0d6774",  # "addnum(uint256)"
            'get_all': "880a3c86",  # "get_all()",
            'get_num': "3e27a8e8",  # "get_num()",
            'get_str': "70f9b8da",  # "get_str()",
            'set_num': "0da665a4",  # "set_num(uint256)",
            'set_str': "438ecee6",  # "set_str(string)",
        }
        super().__init__(contract_address, func_hashes, qtum_rpc)

    def add_num(self, a):
        return self.callcontract(func_name='add_num', input_types=['uint256'], input_values=[a], output_types=['uint256'])

    def get_all(self):
        return self.callcontract(func_name='get_all', input_types=None, input_values=None, output_types=['uint256', 'string'])

    def get_num(self):
        return self.callcontract(func_name='get_num', input_types=None, input_values=None, output_types=['uint256'])

    def get_str(self):
        return self.callcontract(func_name='get_str', input_types=None, input_values=None, output_types=['string'])

    def set_num(self, num):
        return self.sendtocontract(func_name='set_num', input_types=['uint'], input_values=[num], output_types=['uint'])

    def set_str(self, str):
        return self.sendtocontract(func_name='set_str', input_types=['string'], input_values=[str], output_types=['string'])


if __name__ == '__main__':
    test_sc = Test_SC(contract_address)

    test_sc.set_send_params({'sender': contract_owner})
    num = int(test_sc.get_num()[0])
    print('current num: ', num)
    print(test_sc.set_num(num+100))

    time.sleep(300)   # takes some time for transaction to make it to the blockchain
    test_sc.reload_rpc()  # broken pipe exception if not reloaded

    num = int(test_sc.get_num()[0])
    print('num after: ', num)
