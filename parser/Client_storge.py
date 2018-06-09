import os
import sys
import logging
from time import sleep
from jsonrpcclient.http_client import HTTPClient
from searchlogs import SearchLogs



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)

import settings


storghost = settings.storageurl
from_i = 153642


class ClientStorge():
    def __init__(self, sotrg_host=None):
        self.history_host = sotrg_host if sotrg_host else storghost
        self.client = HTTPClient(self.history_host)

    def insert_offer(self, cid=None, buyer_addr=None, price=None):
        if cid and buyer_addr and price:
            request = self.client.request(method_name="insertoffer", 
                                    cid=cid, buyer_addr=buyer_addr, price=price)
            return request
        else:
            return {2: "Missing parameter"}

    def get_offer(self, cid=None, buyer_addr=None):
        if cid and buyer_addr:
            request = self.client.request(method_name="getoffer", 
                                    cid=cid, buyer_addr=buyer_addr)
            return request
        else:
            return {2: "Missing parameter"}

    def update_offer(self, txid=None, flag=None):
        if txid:
            request = self.client.request(method_name="updateoffer", 
                                                    txid=txid, flag=flag)
            return request
        else:
            return {2: "Missing parameter"}

    def mailed_confirm(self, cid=None, buyer_address=None, price=None):
        if cid and buyer_address and price:
            request = self.client.request(method_name="mailedconfirm", 
                                        cid=cid, buyer_address=buyer_address, price=price)
            return request
        else:
            return {2: "Missing parameter"}

    def update_users_content(self, txid=None, cid=None):
        if cid and txid:
            request = self.client.request(method_name="updateuserscontent", 
                                                        cid=cid, txid=txid)
            return request
        else:
            return {2: "Missing parameter"}


def block_cl(from_i, to_i, obj_searchlogs, client):
    searchlog = obj_searchlogs.storge(from_i, to_i, {"addresses": ["52b81892235027453bcdbc2ec25ec7253c531efc"]},
                                      {"topics": ["38a9262fedac02428e492594acec49680f630e226196536d6996dafd344db1ea"]})
    for search in searchlog:
        txid = search[0]
        address = search[1]
        cid = search[2]
        price = search[3]
        #print(search)
        result = client.update_offer(txid, 1)
        if "error" not in result.keys():
            client.mailed_confirm(cid, address, price)
        else:
            pass


def new_offer(from_i, to_i, obj_searchlogs, client):
    searchlog = obj_searchlogs.storge(from_i, to_i, {"addresses": ["52b81892235027453bcdbc2ec25ec7253c531efc"]},
                                      {"topics": ["9170c205402f594bf92e77397182d7d82ef0df80da3629a76e4f0b56852644b7"]})
    for search in searchlog:
        tx_hash = search[0]
        cid = search[1]
        result = client.update_users_content(tx_hash, cid)



def conection_stor():
    while True:
        try:
            cli = ClientStorge(storghost)
            return cli
        except:
            sleep(1)


def conection_search():
    while True:
        try:
            cli = SearchLogs()
            cli.getblockcount()
            return cli
        except:
            #print("Qtum CRASH")
            sleep(1)


def main_code(from_i):
    client = conection_stor()
    obj_searchlogs = conection_search()
    to_i = obj_searchlogs.getblockcount()
    block_cl(from_i, to_i, obj_searchlogs, client)
    new_offer(from_i, to_i, obj_searchlogs, client)
    from_i = to_i
    while True:
        #print(obj_searchlogs.getblockcount())
        try:
            getlastblock = obj_searchlogs.getblockcount()
            if getlastblock >= from_i:
                block_cl(from_i, from_i, obj_searchlogs, client)
                new_offer(from_i, from_i, obj_searchlogs, client)
                from_i += 1
                print(from_i)
                #logging.debug(i)
            else:
                sleep(1)
        except:
            obj_searchlogs = conection_search()
            sleep(1)


if __name__ == "__main__":
    '''
    obj_searchlogs = SearchLogs()
    searchlog = obj_searchlogs.searchlogs(0, -1, {"addresses": ["363d33ed942bd543b073101fa6e5ee00aa67cbad"]})
    #print(searchlog)
    client = ClientHistory()
    for i in searchlog:
        insert_data = client.insert_data( **{'field1': i})
    select_data = client.select_data("searchlogs")
    #print(select_data)
    '''
    main_code(from_i)
