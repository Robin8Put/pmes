from tornado_components.web import SignedHTTPClient
from settings_file import *


class ClientBalance():
    """ Client for balance
    """
    def __init__(self, host=None):
        self.host = host if host else balance_server
        self.client = SignedHTTPClient(self.host)

    def get_balance(self, uids=None, coin_id=None):
        # get balance for uid
        if uids:
            request = self.client.request(method_name="getbalance",
                                          address=uids,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def inc_balance(self, uids=None, amount=.0, coin_id=None):
        # increment for uid
        if uids:
            request = self.client.request(method_name="incbalance",
                                          address=uids,
                                          amount=amount,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def dec_balance(self, uids=None, amount=.0, coin_id=None):
        # decrement for uid
        if uids:
            request = self.client.request(method_name="decbalance",
                                          address=uids,
                                          amount=amount,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}

    def set_balance(self, uid, amount):
        return self.client.set_balance(uid, amount)

    def confirm_balance(self, txid=None, buyer_address=None, cid=None, coin_id=None):
        if txid and buyer_address and cid:
            request = self.client.request(method_name="confirmbalance",
                                          txid=txid,
                                          cid=cid,
                                          buyer_address=buyer_address,
                                          coinid=coin_id)
            return request
        else:
            return {2: "Missing name uid"}
