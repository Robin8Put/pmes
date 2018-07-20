from jsonrpcclient.http_client import HTTPClient
from settings_file import *


class ClientStorge():
    def __init__(self, sotrg_host=None):
        self.history_host = sotrg_host if sotrg_host else storghost
        self.client = HTTPClient(self.history_host)

    def insert_offer(self, cid=None, buyer_addr=None, price=None, coin_id=None):
        if cid and buyer_addr and price:
            try:
                request = self.client.request(method_name="insertoffer",
                                              cid=cid,
                                              buyer_address=buyer_addr,
                                              price=price,
                                              coinid=coin_id)
                return request
            except:
                print("Erorr from insertoffer")
        else:
            return {2: "Missing parameter"}

    def get_offer(self, cid=None, buyer_addr=None, coin_id=None):
        if cid and buyer_addr:
            try:
                request = self.client.request(method_name="getoffer",
                                              cid=cid,
                                              buyer_address=buyer_addr,
                                              coinid=coin_id)
                return request
            except:
                print("Erorr from getoffer")
        else:
            return {2: "Missing parameter"}

    def update_offer(self, txid=None, coin_id=None):
        if txid:
            try:
                request = self.client.request(method_name="updateoffer",
                                              txid=txid,
                                              coinid=coin_id)
                return request
            except Exception as e:
                print("Erorr from updateoffer", e)
        else:
            return {2: "Missing parameter"}

    def mailed_confirm(self, cid=None, buyer_address=None, offer_type=None, price=None, coin_id=None):
        if cid and buyer_address and price:
            try:
                request = self.client.request(method_name="mailedconfirm",
                                              cid=cid,
                                              buyer_address=buyer_address,
                                              price=price,
                                              offer_type=offer_type,
                                              coinid=coin_id)
                return request
            except Exception as e:
                return e
        else:
            return {2: "Missing parameter"}

    def update_users_content(self, txid=None, coin_id=None):
        if txid:
            try:
                request = self.client.request(method_name="updateuserscontent",
                                              txid=txid,
                                              coinid=coin_id)
                return request
            except:
                print("Erorr from updateuserscontent")
        else:
            return {2: "Missing parameter"}

    def update_review(self, txid=None, coin_id=None):
        if txid:
            try:
                request = self.client.request(method_name="updatereview",
                                              txid=txid,
                                              coinid=coin_id)
                return request
            except:
                print("Erorr from updatereview")
        else:
            return {2: "Missing parameter"}
