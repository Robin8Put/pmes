from Parsing import Parsing_block, Table_new
from bitcoinrpc.authproxy import AuthServiceProxy
from jsonrpcclient.http_client import HTTPClient
from time import sleep
from daemon_email import Daemon
from pprint import pprint
import sys
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not BASE_DIR in sys.path:
    sys.path.append(BASE_DIR)

import settings


logging.basicConfig(level=logging.CRITICAL, filename="one_coin.log", format="%(message)s")
balance_server = settings.balanceurl
qtum_server = "http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018")
db_name="pars"
collection="data3"
from_block = 146400


class ClientHistory():
    def __init__(self, history_host=None):
        self.history_host = history_host if history_host else balance_server
        self.client = HTTPClient(self.history_host)

    def getbalance(self, uids=None, coin_id="QTUM"):
        if uids:
            request = self.client.request(method_name="getbalance", address=uids)
            return request
        else:
            return {2: "Missing name uid"}

    def incbalance(self, uids=None, amount=0, coin_id="QTUM"):
        if uids:
            request = self.client.request(method_name="incbalance", address=uids, amount=amount)
            return request
        else:
            return {2: "Missing name uid"}

    def decbalance(self, uids=None, amount=0, coin_id="QTUM"):
        if uids:
            request = self.client.request(method_name="decbalance", address=uids, amount=amount)
            return request
        else:
            return {2: "Missing name uid"}

    def set_balance(self, uid, amount):
        return self.client.set_balance(uid, amount)


class ParsingBlock(Parsing_block):
    def __init__(self, from_block=0, db_name="pars", collection="data3", to_block=-1):
        self.client = ClientHistory()
        self.from_block = from_block
        self.to_block = to_block
        self.qtum = AuthServiceProxy(qtum_server)
        self.db_wallet = Table_new(db_name, collection)

    def check(self, vout):
        try:
            for vout_i in vout:
                try:
                    script_pub_key = vout_i["scriptPubKey"]
                    addresses = script_pub_key["addresses"]
                    value = vout_i["value"]
                    value_float = float(value)
                    value_int = int(value * (10 ** 8))
                    for adr in addresses:
                        data = self.client.getbalance(adr)
                        if data == {'error': 404}:
                            pass
                        else:
                            db_coin = self.db_wallet.insert_new(**{"adr": adr, "value": value_int})
                            update_data_1 = self.client.incbalance(adr, value_float)
                            #logging.critical(update_data_1)
                except:
                    pass
        except:
            pass

    def decode_raw_transaction_vout(self, encoded_datas=None):
        try:
            if not encoded_datas:
                encoded_datas = self.get_raw_transaction()
            for encoded_data in encoded_datas:
                transaction_data = self.qtum.decoderawtransaction(encoded_data)
                vin = transaction_data["vin"]
                vout = transaction_data["vout"]
                self.check(vout)
            self.show_db()
        except:
            pass

    def getblockcount(self):
        return self.qtum.getblockcount()


def server_w(from_i):
    while True:
        try:
            data = ParsingBlock()
            best_block = data.getblockcount()
            if best_block >= from_i:
                pars = ParsingBlock(from_i, db_name, collection)
                logging.critical(from_i)
                getblock = pars.get_transaction_in_block()
                get_raw_transaction = pars.get_raw_transaction()
                decode_raw_transaction = pars.decode_raw_transaction_vout()
                from_i += 1
            else:
                sleep(1)
        except:
            logging.warning("\n[+] -- Error while connecting to blockchain.\n")
            sleep(10)        


class MyDaemon(Daemon):
    def run(self):
        # main program for demonizing
        server_w(from_block)


if __name__ == "__main__":
    # initiation command for work from daemon
    daemon = MyDaemon('/tmp/daem1.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

