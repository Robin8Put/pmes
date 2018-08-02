# Built-ins
import os
import json
import logging

# Third-party
from jsonrpcserver.aio import methods
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from solc import compile_source, compile_files, link_code

from robin8.qrc20_sc import Qrc20

from robin8.qtum_contract_handler import QtumContractHandler

from config import base_blockchains, hosts, erc20_abi, contract_addresses, qtum_hot_wallet, decimals, decimals_k, erc20_code, \
    deploy_settings


class AbstractWithdraw(object):

    def __init__(self):
        self.reload_connections()

    def reload_connections(self):
        self.connections = {}
        for coinid, conn in hosts.items():
            self.connections.update({coinid: AuthServiceProxy(conn)})

    def error_403(self, reason):
        return {"error": 403, "reason":"Withdraw service. " + reason}

    def error_400(self, reason):
        return {"error": 400, "reason":"Withdraw service. " + reason}

    def error_404(self, reason):
        return {"error": 404, "reason":"Withdraw service. " + reason}


    def validate(self, *args, **kwargs):

        if not kwargs:
            self.error_400("Validate. Missed parameters.")
            return

        message = kwargs.get("message")

        if message and isinstance(message, str):
            kwargs = json.loads(message)
        elif message and isinstance(message, dict):
            kwargs = message

        amount = kwargs.get("amount")
        if amount and not isinstance(amount, int):
            self.error_400("Validate. Not valid amount")
            return

        coinid = kwargs.get("coinid")
        if coinid not in hosts.keys():
            self.error_403("Validate. Not valid coinid")

        total_supply = kwargs.get('total_supply')
        if total_supply and not isinstance(amount, int):
            self.error_400("Validate. Not valid total_supply")
            return



class Withdraw(AbstractWithdraw):

    async def create_token(self, *args, **kwargs):

        token_name = kwargs.get('token_name')
        token_symbol = kwargs.get('token_symbol')
        total_supply = kwargs.get('total_supply')
        token_decimals = kwargs.get('decimals')
        blockchain = kwargs.get('blockchain')
        is_burnable = kwargs.get('is_burnable')
        is_mintable = kwargs.get('is_mintable')

        if blockchain == 'QTUMTEST':
            formatted_code = erc20_code.format(token_name=token_name, token_symbol=token_symbol,
                                               token_decimals=token_decimals, total_supply=total_supply)

            contract_code = compile_source(formatted_code)['<stdin>:%s' % token_name]['bin']

            contract_handler = QtumContractHandler.from_http_provider(hosts['QTUMTEST'], None, '{}')
            contract_handler.set_send_params({
                'gasLimit': deploy_settings['gasLimit'],
                'gasPrice': deploy_settings['gasPrice'],
                'sender': qtum_hot_wallet
            })

            return contract_handler.deploy_contract(contract_code)
        else:
            return {'error': 'Unsupported blockchain'}


    async def withdraw(self, *args, **kwargs):
        """
        Withdraw funds to user wallet

        Accepts:
            - coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
            - address [string] withdrawal address (in hex for tokens)
            - amount [int]     withdrawal amount multiplied by decimals_k (10**8)
        Returns dictionary with following fields:
            - txid [string]
        """
        logging.debug("\n\n[+] -- Withdraw debugging. ")
        super().validate(*args, **kwargs)
        super().reload_connections()


        coinid = kwargs.get("coinid")
        address = kwargs.get("address")
        amount = int(kwargs.get("amount"))

        connection = self.connections[coinid]

        if coinid in ['BTCTEST', 'LTCTEST', 'QTUMTEST']:
            txid = connection.sendtoaddress(address, str(amount/decimals_k))
        elif coinid == 'PUTTEST':
            handler = Qrc20.from_connection(connection, contract_addresses['PUTTEST'], erc20_abi)
            handler.set_send_params({'sender': qtum_hot_wallet})
            txid = handler.transfer(address, amount)['txid']
            logging.debug(txid)

        return {'txid': txid}

withdraw_handler = Withdraw()


@methods.add
async def withdraw(*args, **kwargs):
    request = await withdraw_handler.withdraw(*args, **kwargs)
    return request

@methods.add
async def create_token(*args, **kwargs):
    request = await withdraw_handler.create_token(*args, **kwargs)
    return request