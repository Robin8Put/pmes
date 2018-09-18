from jsonrpcclient.http_client import HTTPClient
from handlers.signature_validator import SignatureValidator
from config import public_key, private_key, check_sig


class WithdrawClient:
    withdraw_endpoint = '/api/'

    def __init__(self, withdraw_server_address):
        self.withdraw_server_address = withdraw_server_address
        self.signature_validator = SignatureValidator(private_key, public_key)

    def withdraw(self, *args, **kwargs):
        """
        Withdraw funds to user wallet

        Accepts:
        - coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
            - address [string] withdrawal address (in hex for tokens)
            - amount [int]     withdrawal amount multiplied by decimals_k (10**8)
        Returns dictionary with following fields:
            - txid [string]
        """

        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)
        if check_sig:
            return client.request('withdraw', self.signature_validator.sign(kwargs))
        else:
            return client.request('withdraw', kwargs)

    def withdraw_bulk(self, *args, **kwargs):
        """
        Withdraw funds to user wallet

        Accepts:
        - coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
            - address [string] withdrawal address (in hex for tokens)
            - amount [int]     withdrawal amount multiplied by decimals_k (10**8)
        Returns dictionary with following fields:
            - txid [string]
        """

        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)
        if check_sig:
            return client.request('withdraw_bulk', self.signature_validator.sign(kwargs))
        else:
            return client.request('withdraw_bulk', kwargs)

    def create_token(self, *args, **kwargs):
        """
        create kol token

        Accepts:
            - token_name [string] token name
            - token_symbol [string] toke symbol
            - total_supply [int]     token total supply
            - decimals [int] token precision from 1 to 18
            - blockchain [string] blockchain to create token on ( QTUMTEST, ETHTEST )
            - is_burnable [Bool] can burn tokens
            - is_mintable [Bool] can create new tokens
        Returns dictionary with following fields:
            - txid [string]
            - address [string]
        """

        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)

        if check_sig:
            return client.request('create_token', self.signature_validator.sign(kwargs))
        else:
            return client.request('create_token', kwargs)

    def withdraw_custom_token(self, *args, **kwargs):
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

        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)
        if check_sig:
            return client.request('withdraw_custom_token', self.signature_validator.sign(kwargs))
        else:
            return client.request('withdraw_custom_token', kwargs)

    def is_valid_address(self, *args, **kwargs):
        """
        check address

        Accepts:
            - address [hex string] (withdrawal address in hex form)
            - coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
        Returns dictionary with following fields:
            - bool [Bool]
        """

        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)

        return client.request('is_valid_address', kwargs)

    def register_token(self, *args, **kwargs):
        """
        Register token

        Accepts:
            - token_name [string]
            - contract_address [hex string]
            - blockchain [string]  token's blockchain (QTUMTEST, ETH)
        Returns dictionary with following fields:
            - success [Bool]
         """
        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)
        if check_sig:
            return client.request('register_token', self.signature_validator.sign(kwargs))
        else:
            return client.request('register_token', kwargs)

    def available_tokens(self, *args, **kwargs):
        """
         Available tokens

        Accepts:
        Returns list of dictionaries that has such fields:
            - _id [string] token name
            - contract_address [hex string]
            - blockchain [string] token's blockchain (QTUMTEST, ETH)
        """

        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)

        return client.request('available_tokens')

    def hot_wallet_history(self, *args, **kwargs):
        """
        Hot wallet history

        Accepts:
        Returns list of dictionaries that has such fields:
            - _id [string] token name
            - contract_address [hex string]
            - blockchain [string] token's blockchain (QTUMTEST, ETH)
        """
        client = HTTPClient(self.withdraw_server_address + self.withdraw_endpoint)

        return client.request('hot_wallet_history')


if __name__ == '__main__':
    withdraw_cli = WithdrawClient('http://localhost:7003')

    # print(withdraw_cli.withdraw(**{
    #             'coinid': 'BTCTEST',
    #             'amount': '1000000',
    #             'address': 'mzf3cMX48ZofXj4AgGFudgWMhnz29965mV',
    #         }))

    # print(withdraw_cli.withdraw(**{
    #             'coinid': 'LTCTEST',
    #             'amount': '100000000',
    #             'address': 'mxfUGpHiEbQsLd9KzWeAD1CVWECU4gSEBd',
    #         }))

    # print(withdraw_cli.withdraw(**{
    #             'coinid': 'QTUMTEST',
    #             'amount': '100000000',
    #             'address': 'qXUfvcyLTJnCeMT5Ub8wX3ABjfSK2v9dbe',
    #         }))

    print(withdraw_cli.withdraw(**{
        'coinid': 'PUT',
        'amount': 1,
        'address': 'QPjthx2L6B4GYead9fKKzCfe1A1TaitTq2',
    }))
    # "jsonrpc": "2.0", "method": "withdraw", "params": {"uid": 14, "coinid": "ETH", "amount": 10000,
    #                                                    "address": "56yujrt756uhj3rtwsj3uwr6u254y", "blockchain": null,
    #                                                    "contract_address": null, "total": 1010000}, "id": 3}

    # print(withdraw_cli.withdraw(**{
    #     "coinid": "ETH", "amount": 10000,
    #     "address": "56yujrt756uhj3rtwsj3uwr6u254y"
    # }))

    # print(withdraw_cli.is_valid_address(**{
    #     'address': 'qPszipAbyhFELfkoFbsnmVu3tSkXVNm9tQ',
    #     'coinid': 'QTUMTEST'
    # }))

    # print(withdraw_cli.withdraw_bulk(**{
    #             'coinid': 'ETH',
    #             'amount': '10000000',
    #             'address': '0x3c593b9fcfdb160be7c7b664bde67c4f85da6cf8',
    #         }))

    # print(withdraw_cli.withdraw_bulk(**{
    #             'coinid': 'OMGRINKEBY',
    #             'amount': '1000000',
    #             'address': '0x54d41894db408c9f31b35bfce0910b525450016f',
    #         }))

    # print(withdraw_cli.create_token(**{
    #     'token_name': 'Temp',
    #     'token_symbol': 'TMP',
    #     'total_supply': '10000000000000000',
    #     'decimals': '8',
    #     'blockchain': 'QTUMTEST',
    #     'is_burnable': False,
    #     'is_mintable': False
    # }))

    # print(withdraw_cli.create_token(**{
    #     'token_name': 'AugurToken',
    #     'token_symbol': 'REP',
    #     'total_supply': '10000000000000000',
    #     'decimals': '8',
    #     'blockchain': 'eTh',
    #     'is_burnable': False,
    #     'is_mintable': False
    # }))

    # print(withdraw_cli.withdraw_custom_token(**{
    #             'contract_address': 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4',
    #             'blockchain': 'QTUMTEST',
    #             'amount': '1000000000',
    #             'address': 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis',
    # }))

    # print(withdraw_cli.withdraw_custom_token(**{
    #             'contract_address': '0x55aE4DDF1F2b69535439aD461CD4C0F3c5116Fc7',
    #             'blockchain': 'ETHRINKEBY',
    #             'amount': '1000000000',
    #             'address': '0x54d41894db408c9f31b35bfce0910b525450016f',
    # }))

    # print(withdraw_cli.register_token(**{
    #     'token_name': 'lol',
    #     'contract_address': '0x55aE4DDF1F2b69535439aD461CD4C0F3c5116Fc7',
    #     'blockchain': 'fsddf'
    # }))
    #
    # tokens = [
    #     {'token_name': 'PUTTEST',
    #      'contract_address': 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4',
    #      'blockchain': 'QTUMTEST'},
    #     {'token_name': 'KTOKENRINKEBY',
    #      'contract_address': '0x0f54d6c9373630c456fb5320545eA0bbbD0e8347',
    #      'blockchain': 'ETHRINKEBY'},
    #     {'token_name': 'OMGRINKEBY',
    #      'contract_address': '0x55aE4DDF1F2b69535439aD461CD4C0F3c5116Fc7',
    #      'blockchain': 'ETHRINKEBY'},
    #     {'token_name': 'REPRINKEBY',
    #      'contract_address': '0x6A732d537DAf79d75EFaeAE286D30FC578Fa98D0',
    #      'blockchain': 'ETHRINKEBY'}
    # ]
    # #
    # for token in tokens:
    #     print(withdraw_cli.register_token(**token))

    # print(withdraw_cli.register_token(**{
    #     'token_name': 'lol',
    #     'contract_address': '0x55aE4DDF1F2b69535439aD461CD4C0F3c5116Fc7',
    #     'blockchain': 'fsddf'
    # }))
    #
    # print(withdraw_cli.available_tokens())

    # print(withdraw_cli.withdraw_bulk(**{
    #     'coinid': 'OMGRINKEBY',
    #     'amount': '1000000',
    #     'address': '0x54d41894db408c9f31b35bfce0910b525450016f',
    # }))

    # print(withdraw_cli.hot_wallet_history())

