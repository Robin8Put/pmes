from abc import abstractmethod, ABCMeta


class Erc20_Interface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def totalSupply(self,):
        return NotImplementedError()

    @abstractmethod
    def balanceOf(self, address):
        return NotImplementedError()

    @abstractmethod
    def allowance(self, from_addr, to_addr):
        return NotImplementedError()

    @abstractmethod
    def transfer(self, to_addr, amount):
        return NotImplementedError()

    @abstractmethod
    def approve(self, addr, amount):
        return NotImplementedError()

    @abstractmethod
    def transferFrom(self, from_addr, to_addr, amount):
        return NotImplementedError()

