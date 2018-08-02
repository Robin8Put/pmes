import requests


class WithrawClient:

    withdrow_endpoint = '/api/'


    def __init__(self, withdraw_server_address):
        self.withdraw_server_address = withdraw_server_address


    def withdraw(self, coinid, address, amount):
        """
        Withdraw funds to user wallet

        Accepts:
        	- coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
        	- address [string] withdrawal address (in hex for tokens)
        	- amount [int]     withdrawal amount multiplied by decimals_k (10**8)
        Returns dictionary with following fields:
        	- txid [string]
        """
        data = {
            'method': 'withdraw',
            'jsonrpc': '2.0',
            'params': {
                'coinid': coinid,
                'amount': amount,
                'address': address,
            },
            'id': 0
        }

        return requests.post(self.withdraw_server_address + self.withdrow_endpoint, json=data).json()

    def create_token(self, token_name, token_symbol, total_supply, decimals, blockchain, is_burnable, is_mintable):
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

        data = {
            'method': 'create_token',
            'jsonrpc': '2.0',
            'params': {
                'token_name': token_name,
                'token_symbol': token_symbol,
                'total_supply': total_supply,
                'decimals': decimals,
                'blockchain': blockchain,
                'is_burnable': is_burnable,
                'is_mintable': is_mintable
            },
            'id': 0
        }

        return requests.post(self.withdraw_server_address + self.withdrow_endpoint, json=data).json()


if __name__ == '__main__':

    withdraw_cli = WithrawClient('http://192.168.1.99:8011')

    # print(withdraw_cli.withdraw('BTCTEST', 'mzf3cMX48ZofXj4AgGFudgWMhnz29965mV', '100000'))

    # print (withdraw_cli.withdraw('PUTTEST', 'FDC1AE05C161833CDF135863E332126E15D7568C', '1000000000'))

    print(withdraw_cli.create_token('My_Test_Token', 'MTN', 1000*10**8, 8, 'QTUMTEST', False, False))