from abc import abstractmethod, ABCMeta


class BlockchainHandler:
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def from_http_provider(cls, http_provider):
        return NotImplementedError()

    @classmethod
    @abstractmethod
    def from_ipc_path(cls, ipc):
        return NotImplementedError()

    @abstractmethod
    def get_last_block_hash(self):
        return NotImplementedError()

    @abstractmethod
    def get_second_last_block_hash(self):
        return NotImplementedError()

    @abstractmethod
    def get_last_block_id(self):
        return NotImplementedError()

    @abstractmethod
    def get_second_last_block_id(self):
        return NotImplementedError()

    @abstractmethod
    def get_block_id(self, height):
        return NotImplementedError()

    @abstractmethod
    def get_block_hash(self, height):
        return NotImplementedError()

    @abstractmethod
    def get_block_count(self):
        return NotImplementedError()

    @abstractmethod
    def get_unspent(self):
        return NotImplementedError()

    @abstractmethod
    def get_accounts(self):
        return NotImplementedError()

    @abstractmethod
    def get_balance(self):
        return NotImplementedError()

    @abstractmethod
    def from_hex_address(self, address):
        return NotImplementedError()
