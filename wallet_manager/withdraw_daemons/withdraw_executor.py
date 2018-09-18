import codecs
import datetime
from pprint import pprint

from bip32keys.bip32addresses import Bip32Addresses
from bitcoinrpc.authproxy import AuthServiceProxy
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.platform.asyncio import AsyncIOMainLoop
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from config import hosts, bitcoinlike_coinids, ethereumlike_coinids, OUTPUTS_PER_TX, decimals_k, hot_wallets,\
    erc20_abi, transfer_settings, WITHDRAW_DELAY, eth_passphrase
from contract_handlers.erc20_sc import Erc20
from contract_handlers.qrc20_sc import Qrc20
from handlers.withdraw_db import DatabaseClient
from handlers.withdraw_validator import WithdrawValidator

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


class WithdrawExecutor:
    def __init__(self):
        self.db = DatabaseClient()
        self.connections = {}
        self.callback = PeriodicCallback(self.execute_withdraws, WITHDRAW_DELAY)
        self.callback.start()
        AsyncIOMainLoop().install()
        ioloop = IOLoop.current()
        ioloop.start()

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

    async def execute_withdraws(self):
        print('reload')
        try:
            self.reload_connections()
        except Exception as e:
            return WithdrawValidator.error_500(str(e))
        print('reloaded')

        query = {
            'timestamp': {'$lte': datetime.datetime.utcnow() - datetime.timedelta(milliseconds=WITHDRAW_DELAY)}
        }

        print('start loop')

        document_count = await self.db.withdraw_requests.count_documents(query)
        print('document_count: ', document_count)

        while document_count != 0:
            withdrawal_requests = {}

            for coinid in bitcoinlike_coinids:
                withdrawal_requests[coinid] = []
            for coinid in ethereumlike_coinids:
                withdrawal_requests[coinid] = []

            cursor = self.db.withdraw_requests.find(query)
            cursor.limit(OUTPUTS_PER_TX)

            to_delete = []
            pprint(await self.db.withdraw_requests.count_documents(query))
            async for withdrawal in cursor:
                if await self.db.executed_withdraws.find_one({'_id': withdrawal['_id']}):
                    to_delete.append(withdrawal)
                    print('deleted', withdrawal)
                else:
                    withdrawal_requests[withdrawal['coinid']].append(withdrawal)
                    print('appended', withdrawal)

            for expired in to_delete:
                await self.db.withdraw_requests.delete_one({'_id': expired['_id']})
                print('deleted')

            for coinid, withdrawals in withdrawal_requests.items():
                if coinid in ('BTCTEST', 'LTCTEST', 'QTUMTEST') and withdrawals:
                    connection = self.connections[coinid]
                    addresses_with_amount = {
                        withdrawal['address']: withdrawal['amount'] / decimals_k for withdrawal in withdrawals
                    }
                    try:
                        txid = connection.sendmany('', addresses_with_amount)

                        for withdrawal in withdrawals:
                            withdrawal['txid'] = txid
                            withdrawal['execution_time'] = datetime.datetime.utcnow()
                            await self.db.executed_withdraws.insert_one(withdrawal)
                            await self.db.withdraw_requests.delete_one({'_id': withdrawal['_id']})
                            print('executed')
                    except Exception as e:
                        pprint(WithdrawValidator.error_500(str(e)))
                        pprint(addresses_with_amount)

                else:
                    for withdrawal in withdrawals:
                        if coinid in ('ETH', 'ETHRINKEBY', 'ETHROPSTEN'):
                            connection = self.connections[coinid]
                            address = Web3.toChecksumAddress(withdrawal['address'])

                            try:
                                txid = connection.eth.sendTransaction({
                                    'to': address,
                                    'from': hot_wallets[coinid],
                                    'value': Web3.toWei(withdrawal['amount'] / decimals_k, 'ether')
                                })
                                txid = encode_hex(txid)[0].decode()
                                withdrawal['txid'] = txid
                                withdrawal['execution_time'] = datetime.datetime.utcnow()
                                await self.db.executed_withdraws.insert_one(withdrawal)
                                await self.db.withdraw_requests.delete_one({'_id': withdrawal['_id']})
                                print('executed')

                            except Exception as e:
                                pprint(WithdrawValidator.error_500(str(e)))
                                pprint(withdrawal)

                        else:
                            token = await self.db.available_tokens.find_one({'_id': coinid})
                            if token is None:
                                pprint(WithdrawValidator.error_500('Unsupported coinid'))

                            elif token['blockchain'] in ('QTUM', 'QTUMTEST'):
                                connection = self.connections[coinid]
                                address = Bip32Addresses.address_to_hex(withdrawal['address'])
                                handler = Qrc20.from_connection(
                                    connection,
                                    token['contract_address'],
                                    erc20_abi
                                )
                                handler.set_send_params({
                                    'gasLimit': transfer_settings[token['blockchain']]['gasLimit'],
                                    'gasPrice': transfer_settings[token['blockchain']]['gasPrice'],
                                    'sender': hot_wallets[coinid]
                                })
                                try:
                                    txid = handler.transfer(address, withdrawal['amount'])['txid']
                                    withdrawal['txid'] = txid
                                    withdrawal['execution_time'] = datetime.datetime.utcnow()
                                    await self.db.executed_withdraws.insert_one(withdrawal)
                                    await self.db.withdraw_requests.delete_one({'_id': withdrawal['_id']})
                                    print('executed')

                                except Exception as e:
                                    pprint(WithdrawValidator.error_500(str(e)))
                                    pprint(withdrawal)

                            elif token['blockchain'] in ('ETHRINKEBY', 'ETH'):
                                connection = self.connections[coinid]
                                address = Web3.toChecksumAddress(withdrawal['address'])
                                handler = Erc20.from_connection(
                                    connection,
                                    token['contract_address'],
                                    erc20_abi
                                )
                                handler.set_send_params({
                                    'gasLimit': transfer_settings[token['blockchain']]['gasLimit'],
                                    'gasPrice': transfer_settings[token['blockchain']]['gasPrice'],
                                    'sender': hot_wallets[coinid]})
                                try:
                                    txid = handler.transfer(address, withdrawal['amount'])['txid']
                                    withdrawal['txid'] = txid
                                    withdrawal['execution_time'] = datetime.datetime.utcnow()
                                    await self.db.executed_withdraws.insert_one(withdrawal)
                                    await self.db.withdraw_requests.delete_one({'_id': withdrawal['_id']})
                                    print('executed')

                                except Exception as e:
                                    pprint(WithdrawValidator.error_500(str(e)))
                                    pprint(withdrawal)

            document_count = await self.db.withdraw_requests.count_documents(query)
            print('document_count: ', document_count)


if __name__ == '__main__':
    WithdrawExecutor()
