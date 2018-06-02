import os
import sys
from jsonrpcclient.http_client import HTTPClient
from searchlogs import SearchLogs
from time import sleep

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not BASE_DIR in sys.path:
    sys.path.append(BASE_DIR)

import settings


from_i = 150072


class ClientStorge():
    def __init__(self, storagehost=None):
        self.history_host = storagehost if storagehost else settings.storageurl
        self.client = HTTPClient(self.history_host)

    def insert_offer(self, cid=None, buyer_addr=None, price=None):
        if cid and buyer_addr and price:
            request = self.client.request(method_name="insertoffer", cid=cid, buyer_addr=buyer_addr, price=price)
            return request
        else:
            return {2: "Missing parameter"}

    def get_offer(self, cid=None, buyer_addr=None):
        if cid and buyer_addr:
            request = self.client.request(method_name="getoffer", cid=cid, buyer_addr=buyer_addr)
            return request
        else:
            return {2: "Missing parameter"}

    def update_offer(self, cid=None, buyer_addr=None, flag=None):
        if cid and buyer_addr:
            request = self.client.request(method_name="updateoffer", cid=cid, buyer_addr=buyer_addr, flag=flag)
            return request
        else:
            return {2: "Missing parameter"}

    def mailed_confirm(self, cid=None, buyer_addr=None, price=None):
        if cid and buyer_addr and price:
            request = self.client.request(method_name="mailedconfirm", cid=cid, buyer_addr=buyer_addr, price=price)
            return request
        else:
            return {2: "Missing parameter"}


def block_cl(from_i, to_i, obj_searchlogs, client):
    searchlog = obj_searchlogs.storge(from_i, to_i, {"addresses": ["52b81892235027453bcdbc2ec25ec7253c531efc"]},
                                      {"topics": ["38a9262fedac02428e492594acec49680f630e226196536d6996dafd344db1ea"]})
    for search in searchlog:
        address = search[0]
        cid = search[1]
        price = search[2]
        print(search)
        result = client.update_offer(cid, address, 1)
        if "error" not in result.keys():
            client.mailed_confirm(cid, address, price)
        else:
            pass


def conection_stor():
    while True:
        try:
            cli = ClientStorge()
            return cli
        except:
            sleep(1)


def conection_search():
    while True:
        try:
            cli = SearchLogs()
            return cli
        except:
            sleep(1)


def main_code(from_i):
    client = conection_stor()
    obj_searchlogs = conection_search()
    to_i = obj_searchlogs.getblockcount()
    block_cl(from_i, to_i, obj_searchlogs, client)
    from_i = to_i
    while True:
        try:
            getlastblock = obj_searchlogs.getblockcount()
            if getlastblock >= from_i:
                block_cl(from_i, from_i, obj_searchlogs, client)
                from_i += 1
                print(from_i)
            else:
                sleep(1)
        except:
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
