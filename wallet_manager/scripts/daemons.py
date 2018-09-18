from bitcoinrpc.authproxy import AuthServiceProxy
from scripts.hd_wallet import create_private_key, create_address
from web3 import Web3, IPCProvider, HTTPProvider
from web3.middleware import geth_poa_middleware
from contract_handlers.qrc20_sc import Qrc20

from config import hosts, testnet_hosts, mainnet_hosts, eth_passphrase, ethereumlike_coinids, \
    bitcoinlike_coinids, \
    contract_addresses, erc20_abi, hot_wallets


def listunspent(connections):
    res = []
    for k, v in connections.items():
        if k in bitcoinlike_coinids:
            res.append(v.listunspent())
        elif k in ['ETH', 'ETHRINKEBY', 'ETHROPSTEN']:
            accounts = v.personal.listAccounts
            res = []
            for a in accounts:
                balance = v.eth.getBalance(a)
                if balance != 0:
                    res.append({'address': a, 'amount': balance})
        elif k in contract_addresses['QTUMTEST'].keys():
            contract_address = contract_addresses['QTUMTEST'][k]
            Qrc20.from_connection(v, contract_address, erc20_abi)

    return res


def import_private_keys(xprivate_key, connections, r):
    for i in r:
        for coinid, conn in connections.items():
            private_key = create_private_key(network=coinid, xprv=xprivate_key, uid=i)['private_key']
            try:
                if coinid in bitcoinlike_coinids:
                    conn.importprivkey(private_key)
                    print(private_key)
                elif k in ethereumlike_coinids:
                    conn.personal.importRawKey(private_key, eth_passphrase)
                    print(private_key)
            except Exception as e:
                print(str(e))


def get_balances(connections):
    res = {}
    for coinid, conn in connections.items():
        amount = 0
        if coinid in bitcoinlike_coinids:
            for output in conn.listunspent():
                amount += output['amount']
        elif coinid in ethereumlike_coinids:
            accounts = conn.personal.listAccounts
            for a in accounts:
                amount += conn.eth.getBalance(a)
        amount = float(amount)
        res[coinid] = amount
    return res


if __name__ == '__main__':

    connections = {}
    for k, v in mainnet_hosts.items():
        if k in ethereumlike_coinids:
            connections[k] = Web3(HTTPProvider(v))
        else:
            connections[k] = AuthServiceProxy(v)

    # print(connections['ETH'].isAddress('0x9cfa33442cc62ce79891ee74cef36d784c8653d0'))
    # print(connections['BTCTEST'].sendmany('', {'mzf3cMX48ZofXj4AgGFudgWMhnz29965mV': 0.001,
    #                                            'n4mTfBLRSaTjXgG5s4ZHQogftG6apwb92P': 0.002}))
    # print(connections['BTCTEST'].sendfrom('mzf3cMX48ZofXj4AgGFudgWMhnz29965mV', hot_wallets['BTCTEST'], '0.015'))
    # print(connections['QTUM'].help())
    # print(connections['BTCTEST'].listwallets())
    # print(connections['QTUM'].dumpprivkey('QeRPVfQVDRngpQZDEkaKVJb3QRFNyU515E'))
    print(connections['QTUM'].sendtoaddress('QeRPVfQVDRngpQZDEkaKVJb3QRFNyU515E', 1))
    # print(connections['QTUM'].importprivkey('KwpSYjtYc4kE2NWcybj1XRNB431JZn74pVXBKmXTshgcuU9Vu6b4'))

    # print(listunspent({'ETH': connections['ETH']}))
    # print(listunspent({'BTCTEST': connections['BTCTEST']}))
    # print(get_balances(connections))
    # import_private_keys('xprv9s21ZrQH143K41ZUuj7bpxQyjxyx9j7jRCdQLdamksvVNN5NSEj2hxnoKmjGFcSY6k3TyXZo78s7bXE4Jf38bXysgyPoE2qTx5fcowFQviv',
    #                     {'QTUM': connections['QTUM']},
    #                     range(0,100))
    # print(create_address(network='LTCTEST', xpub=exchange_xpublic_key, uid=2))
    #
    # connectoin = connections['ETH']
    # address = '0xa82E57390cEbdbBE56AB408Dc967EA068216dc19'
    # eth_hot_wallet = '0xa82E57390cEbdbBE56AB408Dc967EA068216dc19'

    # connectoin.personal.unlockAccount(eth_hot_wallet, eth_passphrase)
    # connectoin.middleware_stack.inject(geth_poa_middleware, layer=0)
    # address = Web3.toChecksumAddress(address)
    # txid = connectoin.eth.sendTransaction(
    #     {'to': address, 'from': eth_hot_wallet, 'value': Web3.toWei(0.01, 'ether')}
    # )
