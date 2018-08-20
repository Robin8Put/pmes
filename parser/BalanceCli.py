import os
import sys
from settings_file import *
import pymongo
import settings

from tornado_components.web import SignedHTTPClient


class ClientBalance():
    """ Client for balance
    """
    def __init__(self, host=None):
        self.host = host if host else settings.balanceurl
        self.client = SignedHTTPClient(self.host)

    def inc_balance(self, address=None, amount=0, coinid=None):
        # increment for uid
        if address:
            request = self.client.request(method_name="add_active",
                                          address=address,
                                          amount=amount,
                                          coinid=coinid)
            return request
        else:
            return {2: "Missing name uid"}

    def dec_balance(self, address=None, amount=0, coinid=None):
        # decrement for uid
        if address:
            request = self.client.request(method_name="sub_active",
                                          address=address,
                                          amount=amount,
                                          coinid=coinid)
            return request
        else:
            return {2: "Missing name uid"}

    def set_balance(self, address, amount):
        return self.client.set_balance(address, amount)

    def confirm_balance(self, txid=None, buyer_address=None, cid=None, coinid=None):
        if txid and buyer_address and cid:
            request = self.client.request(method_name="confirmbalance",
                                          txid=txid,
                                          cid=cid,
                                          buyer_address=buyer_address,
                                          coinid=coinid)
            return request
        else:
            return {2: "Missing name uid"}


class TablePars():
    def __init__(self, host=None, db_name=None):
        # Set database parameters
        self.client = settings.SYNC_DB_CLIENT
        self.database = self.client[db_name]

    def check_address(self, address=None, coinid=None):
        address_check = {"address": address}
        collection = self.database[coinid]
        result = collection.find_one(address_check)
        if result:
            return result
        else:
            return None

    def find(self):
        return self.database["ETH"].find().count()


if __name__ == '__main__':
    client = ClientBalance()
    client.confirm_balance()