from robin8.qtum_contract_handler import QtumContractHandler
from robin8.erc20_interface import Erc20_Interface


class Qrc20(Erc20_Interface, QtumContractHandler):

    def totalSupply(self,):
        return self.call_contract(func_name='totalSupply', input_types=None, input_values=None,
                                  output_types=['uin256'])

    def balanceOf(self, address):
        return self.call_contract(func_name='balanceOf', input_types=['address'], input_values=[address],
                                  output_types=['uint256'])

    def allowance(self, from_addr, to_addr):
        return self.call_contract(func_name='allowance', input_types=['address', 'address'], input_values=[from_addr, to_addr],
                                  output_types=['uint256'])

    def transfer(self, to_addr, amount):
        return self.send_to_contract(func_name='transfer', input_types=['address', 'uint256'], input_values=[to_addr, amount],
                                     output_types=['bool'])

    def approve(self, addr, amount):
        return self.send_to_contract(func_name='approve', input_types=['address', 'uint256'], input_values=[addr, amount],
                                     output_types=['bool'])

    def transferFrom(self, from_addr, to_addr, amount):
        return self.send_to_contract(func_name='transferFrom', input_types=['address', 'address', 'uint256'], input_values=[from_addr, to_addr, amount],
                                     output_types=['bool'])

