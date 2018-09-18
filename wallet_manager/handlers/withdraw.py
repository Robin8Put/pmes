import codecs
import datetime
from pprint import pprint

import rlp
import sha3
import tornado

from tornado.ioloop import IOLoop
from tornado.ioloop import PeriodicCallback

from handlers.abstract_withdraw import AbstractWithdraw
from handlers.withdraw_validator import WithdrawValidator

from config import ethereumlike_coinids, bitcoinlike_coinids, erc20_code, deploy_settings, transfer_settings, \
    erc20_abi, contract_addresses, decimals_k, hot_wallets, qtum_tokens, ethereum_tokens, WITHDRAW_DELAY, OUTPUTS_PER_TX

from web3 import Web3

from bip32keys.bip32addresses import Bip32Addresses
from dev_settings import networks

from contract_handlers.qrc20_sc import Qrc20
from contract_handlers.erc20_sc import Erc20

from contract_handlers.qtum_contract_handler import QtumContractHandler

from solc import compile_source, compile_files, link_code

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


def make_contract_address(sender, nonce):
    sender = codecs.decode(sender[2:], 'hex')
    rlp_encode = rlp.encode([sender, nonce])
    sha3_keccak = sha3.keccak_256(rlp_encode)
    full_hex = sha3_keccak.hexdigest()
    normal_hex = full_hex[-40:]
    result = "0x" + normal_hex
    return result


class Withdraw(AbstractWithdraw):

    def __init__(self):
        super().__init__()
        tornado.ioloop.IOLoop.current().run_sync(self.register_default_tokens)

    async def register_default_tokens(self):

        tokens = [
            {'_id': 'PUT',
             'contract_address': '4060e21ac01b5c5d2a3f01cecd7cbf820f50be95',
             'blockchain': 'QTUM'}
        ]
        for token in tokens:
            if await self.db.available_tokens.find_one({'_id': token['_id']}) is None:
                await self.db.available_tokens.insert_one(token)

    async def is_valid_address(self, *args, **kwargs):
        coinid = kwargs.get('coinid')
        address = kwargs.get('address')

        if address is None or coinid is None:
            return False

        if coinid in ethereumlike_coinids:
            return Web3.isAddress(address)
        elif coinid in bitcoinlike_coinids:
            try:
                Bip32Addresses.verify_address(address)
                if Bip32Addresses.get_magic_byte(address) != networks[coinid].PUBKEY_ADDRESS:
                    return False
            except:
                return False
        return True

    async def create_token(self, *args, **kwargs):

        try:
            super().reload_connections()
        except Exception as e:
            return WithdrawValidator.error_500(str(e))

        token_name = kwargs.get('token_name')
        token_symbol = kwargs.get('token_symbol')
        total_supply = kwargs.get('total_supply')
        token_decimals = kwargs.get('decimals')
        blockchain = kwargs.get('blockchain')
        is_burnable = kwargs.get('is_burnable')
        is_mintable = kwargs.get('is_mintable')
        token_class_name = token_name.replace(' ', '_')

        await self.db.create_token_requests.insert_one({
            'token_name': token_name,
            'token_symbol': token_symbol,
            'total_supply': total_supply,
            'token_decimals': token_decimals,
            'blockchain': blockchain,
            'is_burnable': is_burnable,
            'is_mintable': is_mintable,
            'timestamp': datetime.datetime.utcnow()
        })

        formatted_code = erc20_code.format(token_name=token_name, token_class_name=token_class_name,
                                           token_symbol=token_symbol, token_decimals=token_decimals,
                                           total_supply=total_supply)

        try:
            contract_code = compile_source(formatted_code)['<stdin>:%s' % token_name]['bin']
        except Exception as e:
            return WithdrawValidator.error_500(str(e))

        if blockchain in ['QTUM', 'QTUMTEST']:
            qtum_connection = self.connections[blockchain]
            contract_handler = QtumContractHandler.from_connection(qtum_connection, None, '{}')
            contract_handler.set_send_params({
                'gasLimit': deploy_settings[blockchain]['gasLimit'],
                'gasPrice': deploy_settings[blockchain]['gasPrice'],
                'sender': hot_wallets[blockchain]
            })
            try:
                result = contract_handler.deploy_contract(contract_code)
            except Exception as e:
                return WithdrawValidator.error_500("Couldn't deploy smart contract. %s" % str(e))

            return result

        elif blockchain in ['ETH', 'ETHRINKEBY', 'ETHROPSTEN']:
            connection = self.connections[blockchain]
            contract_address = make_contract_address(hot_wallets[blockchain],
                                                     connection.eth.getTransactionCount(hot_wallets[blockchain]))
            custom_token_contract = connection.eth.contract(abi=erc20_abi, bytecode=contract_code)
            try:
                contract_data = custom_token_contract.constructor().buildTransaction(transaction={
                    'from': hot_wallets[blockchain],
                    'gas': deploy_settings[blockchain]['gasLimit'],
                    'gasPrice': deploy_settings[blockchain]['gasPrice'],
                }
                )
            except Exception as e:
                return WithdrawValidator.error_500('Error building transaction. %s' % str(e))
            try:
                tx_hash = connection.eth.sendTransaction(contract_data)
            except Exception as e:
                return WithdrawValidator.error_500("Error sending transaction. %s" % str(e))
            if tx_hash is None:
                return WithdrawValidator.error_500("Error sending transaction. Hash is None")
            tx_hex = encode_hex(tx_hash)[0].decode()

            return {'txid': tx_hex, 'contract_address': contract_address}
        else:
            return WithdrawValidator.error_403('Unsupported blockchain')

    async def withdraw_bulk(self, *args, **kwargs):
        """
       Withdraw funds requests to user wallet

       Accepts:
           - coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
           - address [string] withdrawal address (in hex for tokens)
           - amount [int]     withdrawal amount multiplied by decimals_k (10**8)
       Returns dictionary with following fields:
           - success [bool]
       """
        await self.db.withdraw_requests.insert_one({
            'coinid': kwargs.get("coinid"),
            'address': kwargs.get("address"),
            'amount': int(kwargs.get("amount")),
            'timestamp': datetime.datetime.utcnow()
        })

        return {'success': True}

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
        try:
            super().reload_connections()
        except Exception as e:
            return WithdrawValidator.error_500(str(e))

        coinid = kwargs.get("coinid")
        address = kwargs.get("address")
        amount = int(kwargs.get("amount"))
        txid = None
        connection = self.connections[coinid]

        if coinid in ['BTCTEST', 'LTCTEST', 'QTUMTEST', 'BTC', 'LTC', 'QTUM']:
            try:
                txid = connection.sendtoaddress(address, str(amount / decimals_k))
            except Exception as e:
                return WithdrawValidator.error_400(str(e))
        elif coinid in ['ETH', 'ETHRINKEBY', 'ETHROPSTEN']:
            address = Web3.toChecksumAddress(address)
            try:
                txid = connection.eth.sendTransaction(
                    {'to': address, 'from': hot_wallets[coinid], 'value': Web3.toWei(amount / decimals_k, 'ether')}
                )
                txid = encode_hex(txid)[0].decode()
            except Exception as e:
                return WithdrawValidator.error_500(str(e))
        else:
            token = await self.db.available_tokens.find_one({'_id': coinid})
            if token is None:
                return WithdrawValidator.error_500('Unsupported coinid')

            elif token['blockchain'] in ('QTUM', 'QTUMTEST'):
                connection = self.connections[coinid]
                address = Bip32Addresses.address_to_hex(address)
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
                print(hot_wallets[coinid])
                try:
                    txid = handler.transfer(address, amount)['txid']
                except Exception as e:
                    return WithdrawValidator.error_500(str(e))

            elif token['blockchain'] in ('ETHRINKEBY', 'ETH'):
                connection = self.connections[coinid]
                address = Web3.toChecksumAddress(address)
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
                    txid = handler.transfer(address, amount)['txid']
                except Exception as e:
                    return WithdrawValidator.error_500(str(e))

        await self.db.executed_withdraws.insert_one({
            'coinid': coinid,
            'address': address,
            'amount': amount,
            'txid': txid,
            'timestamp': datetime.datetime.utcnow(),
            'execution_time': datetime.datetime.utcnow()
        })
        return {'txid': txid}

    async def withdraw_custom_token(self, *args, **kwargs):
        """
        Withdraw custom token to user wallet

        Accepts:
            - address [hex string] (withdrawal address in hex form)
            - amount [int] withdrawal amount multiplied by decimals_k (10**8)
            - blockchain [string]  token's blockchain (QTUMTEST, ETH)
            - contract_address [hex string] token contract address
        Returns dictionary with following fields:
            - txid [string]
        """
        try:
            super().reload_connections()
        except Exception as e:
            return WithdrawValidator.error_500(str(e))

        address = kwargs.get("address")
        amount = kwargs.get("amount")
        blockchain = kwargs.get("blockchain")
        contract_address = kwargs.get("contract_address")

        await self.db.withdraw_custom_token_requests.insert_one({
            'address': address,
            'amount': amount,
            'blockchain': blockchain,
            'contract_address': contract_address,
            'timestamp': datetime.datetime.utcnow()
        })

        connection = self.connections[blockchain]

        if blockchain in ['QTUMTEST', 'QTUM']:
            address = Bip32Addresses.address_to_hex(address)
            handler = Qrc20.from_connection(connection, contract_address, erc20_abi)
            handler.set_send_params({
                'gasLimit': transfer_settings[blockchain]['gasLimit'],
                'gasPrice': transfer_settings[blockchain]['gasPrice'],
                'sender': hot_wallets[blockchain]
            })
            try:
                txid = handler.transfer(address, amount)['txid']
            except Exception as e:
                return WithdrawValidator.error_500(str(e))

        elif blockchain in ['ETH', 'ETHRINKEBY', 'ETHROPSTEN']:
            address = Web3.toChecksumAddress(address)
            contract_address = Web3.toChecksumAddress(contract_address)
            handler = Erc20.from_connection(connection, contract_address, erc20_abi)
            handler.set_send_params({
                'gasLimit': transfer_settings[blockchain]['gasLimit'],
                'gasPrice': transfer_settings[blockchain]['gasPrice'],
                'sender': hot_wallets[blockchain]
            })
            try:
                txid = handler.transfer(address, amount)['txid']
            except Exception as e:
                return WithdrawValidator.error_500(str(e))
        else:
            return WithdrawValidator.error_403('Unsupported blockchain')

        return {'txid': txid}

    async def register_token(self, *args, **kwargs):
        try:
            await self.db.available_tokens.insert_one({
                "_id": kwargs.get("token_name"),
                "contract_address": kwargs.get("contract_address"),
                "blockchain": kwargs.get("blockchain")
            })

        except Exception as e:
            return WithdrawValidator.error_500(str(e))
        return {'success': True}

    async def available_tokens(self, *args, **kwargs):
        try:
            token_names = []
            async for token in self.db.available_tokens.find():
                token_names.append(token)
            return token_names

        except Exception as e:
            return WithdrawValidator.error_500(str(e))

    async def hot_wallet_history(self, *args, **kwargs):
        try:
            executed_requests = []
            async for executed in self.db.executed_withdraws.find({}, {'_id': 0, 'timestamp': 0}):
                executed['execution_time'] = executed['execution_time'].isoformat()
                executed_requests.append(executed)
            return executed_requests

        except Exception as e:
            return WithdrawValidator.error_500(str(e))
