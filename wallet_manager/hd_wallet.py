from pywallet import wallet
from pywallet.wallet import get_network
from pywallet.utils import (
    Wallet, HDPrivateKey, HDKey
)

def create_private_key(network, xprv, uid, path=0):
    assert xprv is not None
    assert uid is not None

    res = {
        "type": network,
        "uid": uid,
    }

    if network == 'ethereum' or network.upper() == 'ETH':
        acct_prv_key = HDKey.from_b58check(xprv)
        keys = HDPrivateKey.from_path(
            acct_prv_key, '{change}/{index}'.format(change=path, index=uid))

        res['private_key'] = keys[-1]._key.to_hex()

        return res

    # else ...
    wallet_obj = Wallet.deserialize(xprv, network=network.upper())
    child_wallet = wallet_obj.get_child(uid, is_prime=False)

    net = get_network(network)
    res['private_key'] = child_wallet.export_to_wif()

    return res

def create_address(network, xpub, uid, path=0):
    assert xpub is not None
    assert uid is not None

    res = {
        "type": network,
        "uid": uid,
    }

    if network == 'ethereum' or network.upper() == 'ETH':
        acct_pub_key = HDKey.from_b58check(xpub)
        keys = HDKey.from_path(
            acct_pub_key, '{change}/{index}'.format(change=path, index=uid))

        res['address'] = keys[-1].address()

        return res

    # else ...
    wallet_obj = Wallet.deserialize(xpub, network=network.upper())
    child_wallet = wallet_obj.get_child(uid, is_prime=False)

    net = get_network(network)
    res['address'] = child_wallet.to_address()

    return res

available_coins = ["BTCTEST", "LTCTEST", "ETH", "QTUMTEST"]
exchange_xpublic_key = "tpubD6NzVbkrYhZ4XFMXfJoNyB8JEpvkCQPNLZRfuhQaSsSurHrMqVKwHvbpD3wHQFTa5U3SBDDPHRhDLmkYfu59Upee8kVSLX8VeKXz4xhBa7z"

def extend_tree(rng):
    res = []
    for i in rng:
        for type in available_coins:
            entry = create_address(type, exchange_xpublic_key, i)
            entry.update(
                {'amount_active': 0, 'amount_frozen': 0}
            )
            res.append(entry)
    return res


if __name__ == '__main__':

    current_depth = 0 # max uid from balance database + 1
    depth = 100       # max uid from mainexchange server + 100

    print(extend_tree(range(current_depth, depth)))




