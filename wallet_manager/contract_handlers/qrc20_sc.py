from contract_handlers.qtum_contract_handler import QtumContractHandler
from contract_handlers.erc20_interface import Erc20_Interface


class Qrc20(Erc20_Interface, QtumContractHandler):

    def totalSupply(self, ):
        return self.call_contract(func_name='totalSupply', input_types=None, input_values=None,
                                  output_types=['uin256'])

    def balanceOf(self, address):
        return self.call_contract(func_name='balanceOf', input_types=['address'], input_values=[address],
                                  output_types=['uint256'])

    def allowance(self, from_addr, to_addr):
        return self.call_contract(func_name='allowance', input_types=['address', 'address'],
                                  input_values=[from_addr, to_addr],
                                  output_types=['uint256'])

    def transfer(self, to_addr, amount):
        return self.send_to_contract(func_name='transfer', input_types=['address', 'uint256'],
                                     input_values=[to_addr, amount],
                                     output_types=['bool'])

    def approve(self, addr, amount):
        return self.send_to_contract(func_name='approve', input_types=['address', 'uint256'],
                                     input_values=[addr, amount],
                                     output_types=['bool'])

    def transferFrom(self, from_addr, to_addr, amount):
        return self.send_to_contract(func_name='transferFrom', input_types=['address', 'address', 'uint256'],
                                     input_values=[from_addr, to_addr, amount],
                                     output_types=['bool'])


if __name__ == '__main__':
    abi = '[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"},{"name":"extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'

    put_address = 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4'
    http_provider = 'http://qtumuser:qtum2018@127.0.0.1:8333'
    handler = Qrc20.from_http_provider(http_provider, put_address, abi)
    handler.set_send_params({'sender': 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'})
    print(handler.transfer('AE438A715E158443D356E4B8AF9A80579D9DAF5D', 10000000000000))
