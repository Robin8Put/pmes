from jsonrpcclient.http_client import HTTPClient
from searchlogs import SearchLogs
from time import sleep


storghost = "http://192.168.1.199:8001/api/storage"
from_i = 153642
addresses = "f63a5d2564a4b291078115f055eda46978cd61fb"
newCID_topic = "14fdb107141cf4fd210e2acfcc2b43094b54d909b94e77b131540b93d42937ce"
newOffer_topic = "d2fb49496cad2d1e30798f48842e124dad6f0c61cc6fb67c18fde37c3ce74dd4"
newReview_topic = "ad88468b4fbb35e2dc97c703f980614af53cc5ee52aa3c8b39d60a685c708241"


class ClientStorge():
    def __init__(self, sotrg_host=None):
        self.history_host = sotrg_host if sotrg_host else storghost
        self.client = HTTPClient(self.history_host)

    def insert_offer(self, cid=None, buyer_addr=None, price=None):
        if cid and buyer_addr and price:
            try:
                request = self.client.request(method_name="insertoffer", cid=cid, buyer_addr=buyer_addr, price=price)
                return request
            except:
                print("Erorr from insertoffer")
        else:
            return {2: "Missing parameter"}

    def get_offer(self, cid=None, buyer_addr=None):
        if cid and buyer_addr:
            try:
                request = self.client.request(method_name="getoffer", cid=cid, buyer_addr=buyer_addr)
                return request
            except:
                print("Erorr from getoffer")
        else:
            return {2: "Missing parameter"}

    def update_offer(self, txid=None):
        if txid:
            try:
                request = self.client.request(method_name="updateoffer", txid=txid, confirmed=True)
                return request
            except:
                print("Erorr from updateoffer")
        else:
            return {2: "Missing parameter"}

    def mailed_confirm(self, cid=None, buyer_addr=None, price=None):
        if cid and buyer_addr and price:
            try:
                request = self.client.request(method_name="mailedconfirm", cid=cid, buyer_address=buyer_addr, price=price)
                return request
            except:
                print("Erorr from mailedconfirm")
        else:
            return {2: "Missing parameter"}

    def update_users_content(self, txid=None, cid=None):
        if cid and txid:
            try:
                request = self.client.request(method_name="updateuserscontent", cid=cid, txid=txid)
                return request
            except:
                print("Erorr from updateuserscontent")
        else:
            return {2: "Missing parameter"}

    def update_review(self, txid=None, confirmed=None):
        if confirmed and txid:
            try:
                request = self.client.request(method_name="updatereview", confirmed=confirmed, txid=txid)
                return request
            except:
                print("Erorr from updatereview")
        else:
            return {2: "Missing parameter"}


def new_offer(from_i, to_i, obj_searchlogs, client):
    searchlog = obj_searchlogs.storge(from_i, to_i, {"addresses": [addresses]},
                                      {"topics": [newOffer_topic]})
    for search in searchlog:
        txid = search[0]
        address = search[1]
        cid = search[2]
        offer_type = search[3]
        price = search[4]
        #print(search)
        #print(search)
        result = client.update_offer(txid)
        if "error" not in result.keys() and result:
            client.mailed_confirm(cid, address, price)
        else:
            pass


def new_cid(from_i, to_i, obj_searchlogs, client):
    searchlog = obj_searchlogs.storge(from_i, to_i, {"addresses": [addresses]},
                                      {"topics": [newCID_topic]})
    for search in searchlog:
        tx_hash = search[0]
        cid = search[1]
        result = client.update_users_content(tx_hash, cid)


def new_review(from_i, to_i, obj_searchlogs, client):
    searchlog = obj_searchlogs.storge(from_i, to_i, {"addresses": [addresses]},
                                      {"topics": [newReview_topic]})
    for search in searchlog:
        tx_hash = search[0]
        result = client.update_users_content(tx_hash, 1)

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
    new_offer(from_i, to_i, obj_searchlogs, client)
    new_cid(from_i, to_i, obj_searchlogs, client)
    from_i = to_i
    while True:
        #print(obj_searchlogs.getblockcount())
        try:
            getlastblock = obj_searchlogs.getblockcount()
            if getlastblock >= from_i:
                new_offer(from_i, from_i, obj_searchlogs, client)
                new_cid(from_i, from_i, obj_searchlogs, client)
                new_review(from_i, from_i, obj_searchlogs, client)
                from_i += 1
                print(from_i)
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
