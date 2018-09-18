from contract_handlers.erc20_interface import Erc20_Interface
from contract_handlers.eth_contract_handler import EthContractHandler


class Erc20(Erc20_Interface, EthContractHandler):

    def totalSupply(self, ):
        return self.contract.functions.totalSupply()

    def balanceOf(self, address):
        return self.contract.functions.balanceOf(address)

    def allowance(self, from_addr, to_addr):
        return self.contract.functions.allowance(from_addr, to_addr)

    def transfer(self, to_addr, amount):
        return self.send_to_contract(self.contract.functions.transfer(to_addr, amount))

    def approve(self, addr, amount):
        return self.send_to_contract(self.contract.functions.approve(addr, amount))

    def transferFrom(self, from_addr, to_addr, amount):
        return self.send_to_contract(self.contract.functions.transferFrom(from_addr, to_addr, amount))
