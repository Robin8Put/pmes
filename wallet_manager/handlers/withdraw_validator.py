from OpenSSL import crypto
import json
import pickle
import codecs

from config import hosts, ethereumlike_coinids, base_blockchains, cold_wallets
from web3 import Web3
import re
import logging

decode_hex = codecs.getdecoder("hex_codec")
encode_hex = codecs.getencoder("hex_codec")


class WithdrawValidator:

    @staticmethod
    def validate_coinid(kwargs):
        coinid = kwargs.get('coinid')
        if coinid is None:
            raise Exception('Coinid not specified')
        kwargs['coinid'] = kwargs['coinid'].upper()
        coinid = kwargs['coinid']
        if coinid not in hosts.keys():
            raise Exception('Unsupported coinid')

    @staticmethod
    def validate_amount(kwargs):
        amount = kwargs.get('amount')
        if amount is None:
            raise Exception('Amount is not specified')
        try:
            kwargs['amount'] = int(kwargs['amount'])
        except:
            raise Exception('Invalid amount')
        amount = kwargs['amount']
        if amount <= 0:
            raise Exception('Invalid amount')

    @staticmethod
    def validate_contract_address(kwargs):
        contract_address = kwargs.get('contract_address')
        if contract_address is None:
            raise Exception('contract address not specified')
        coinid = kwargs.get('coinid')
        if coinid in ethereumlike_coinids:
            try:
                kwargs['contract_address'] = Web3.toChecksumAddress(contract_address)
            except:
                raise Exception('Invalid address')

    @staticmethod
    def validate_blockchain(kwargs):
        try:
            kwargs['blockchain'] = kwargs['blockchain'].upper()
        except:
            raise Exception('blockchain parameter not specified')

        blockchain = kwargs['blockchain']
        if blockchain not in base_blockchains:
            raise Exception('Unsupported blockchain')

    @staticmethod
    def validate_token_name(kwargs):
        token_name = kwargs.get('token_name')
        if token_name is None:
            raise Exception('token_name parameter not specified')
        if not re.match('^[a-z A-Z]{1,30}$', token_name):
            raise Exception('invalid sequence in token name')

    @staticmethod
    def validate_token_symbol(kwargs):
        token_symbol = kwargs.get('token_symbol')
        if token_symbol is None:
            raise Exception('token_symbol parameter not specified')
        if not re.match('^[a-zA-Z]{1,5}$', token_symbol):
            raise Exception('invalid sequence in token_symbol')

    @staticmethod
    def validate_decimals(kwargs):
        decimals = kwargs.get('decimals')
        if decimals is None:
            raise Exception('decimals paramater is not specified')
        try:
            decimals = int(decimals)
        except:
            raise Exception('decimals must be integer')

        if decimals < 1 or decimals > 18:
            raise Exception('invalid decimals')

    @staticmethod
    def validate_total_supply(kwargs):
        total_supply = kwargs.get('total_supply')
        if total_supply is None:
            raise Exception('total_supply not specified')
        try:
            total_supply = int(total_supply)
        except:
            raise Exception('total_supply must be integer')

        if total_supply < 1:
            raise Exception('invalid total_supply')

    @staticmethod
    def validate_address(kwargs):
        address = kwargs.get('address')
        if address is None:
            raise Exception('Address is not specified')
        coinid = kwargs.get('coinid')
        blockchain = kwargs.get('blockchain')
        if coinid is None and blockchain is not None:
            coinid = blockchain

        if coinid in ethereumlike_coinids:
            try:
                kwargs['address'] = Web3.toChecksumAddress(address)
            except:
                raise Exception('Invalid address')

        return True

    @staticmethod
    def validate_cold_wallet_address(kwargs):
        try:
            kwargs['address'] = cold_wallets[kwargs['coinid']]
        except:
            raise Exception('Invalid coinid')
    @staticmethod
    def validate_withdraw(kwargs):
        WithdrawValidator.validate_coinid(kwargs)
        WithdrawValidator.validate_amount(kwargs)
        WithdrawValidator.validate_address(kwargs)

    @staticmethod
    def validate_create_token(kwargs):
        WithdrawValidator.validate_total_supply(kwargs)
        WithdrawValidator.validate_decimals(kwargs)
        WithdrawValidator.validate_token_name(kwargs)
        WithdrawValidator.validate_token_symbol(kwargs)
        WithdrawValidator.validate_blockchain(kwargs)

    @staticmethod
    def validate_withdraw_custom_token(kwargs):
        WithdrawValidator.validate_contract_address(kwargs)
        WithdrawValidator.validate_blockchain(kwargs)
        WithdrawValidator.validate_amount(kwargs)
        WithdrawValidator.validate_address(kwargs)

    @staticmethod
    def validate_register_token(kwargs):
        WithdrawValidator.validate_token_name(kwargs)
        WithdrawValidator.validate_contract_address(kwargs)
        WithdrawValidator.validate_blockchain(kwargs)

    @staticmethod
    def validate_is_valid_address(kwargs):
        WithdrawValidator.validate_coinid(kwargs)

    @staticmethod
    def error_403(reason):
        logging.error(reason)
        return {"error": 403, "reason": "Withdraw service. " + reason}

    @staticmethod
    def error_400(reason):
        logging.error(reason)
        return {"error": 400, "reason": "Withdraw service. " + reason}

    @staticmethod
    def error_404(reason):
        logging.error(reason)
        return {"error": 404, "reason": "Withdraw service. " + reason}

    @staticmethod
    def error_500(reason):
        logging.error(reason)
        return {"error": 500, "reason": "Withdraw service. " + reason}
