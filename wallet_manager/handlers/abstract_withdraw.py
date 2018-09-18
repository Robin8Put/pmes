from motor import MotorClient

from config import hosts, bitcoinlike_coinids, ethereumlike_coinids, hot_wallets, eth_passphrase

from web3 import Web3, IPCProvider, HTTPProvider
from web3.middleware import geth_poa_middleware

from bitcoinrpc.authproxy import AuthServiceProxy

from handlers.withdraw_db import DatabaseClient


class AbstractWithdraw:

    def __init__(self):
        self.connections = {}
        self.db = DatabaseClient()

    def reload_connections(self):
        for coinid, conn in hosts.items():
            if coinid in bitcoinlike_coinids:
                try:
                    self.connections.update({coinid: AuthServiceProxy(conn)})
                except Exception as e:
                    raise Exception("Can't connect to %s daemon. Check config file. %s" % (coinid, str(e)))
            elif coinid in ethereumlike_coinids:
                try:
                    eth_conn = Web3(HTTPProvider(conn))
                except Exception as e:
                    raise Exception("Can't connect to %s daemon. Check config file. %s" % (coinid, str(e)))

                try:
                    eth_conn.personal.unlockAccount(hot_wallets[coinid], eth_passphrase)
                except Exception as e:
                    raise Exception("Can't unlock hot wallet account. Eth passpharse is incorrect. %s" % str(e))

                eth_conn.middleware_stack.inject(geth_poa_middleware, layer=0)
                self.connections.update({coinid: eth_conn})
