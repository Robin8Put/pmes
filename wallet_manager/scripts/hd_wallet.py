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

    if network == 'PUT':
        wallet_obj = Wallet.deserialize(xprv, network='QTUM')
    elif network == 'PUTTEST':
        wallet_obj = Wallet.deserialize(xprv, network='QTUMTEST')
    else:
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

    if network == 'ethereum' or network.upper() in ['ETH', 'ETHRINKEBY', 'ETHROPSTEN']:
        acct_pub_key = HDKey.from_b58check(xpub)
        keys = HDKey.from_path(
            acct_pub_key, '{change}/{index}'.format(change=path, index=uid))

        res['address'] = keys[-1].address()

        return res

    # else ...
    if network == 'PUT':
        wallet_obj = Wallet.deserialize(xpub, network='QTUM')
    elif network == 'PUTTEST':
        wallet_obj = Wallet.deserialize(xpub, network='QTUMTEST')
    else:
        wallet_obj = Wallet.deserialize(xpub, network=network.upper())
    child_wallet = wallet_obj.get_child(uid, is_prime=False)

    net = get_network(network)
    res['address'] = child_wallet.to_address()

    return res


available_coins = ["BTCTEST", "LTCTEST", "ETH", "QTUMTEST", "PUTTEST", "ETHRINKEBY"]
exchange_xpublic_key = "tpubD6NzVbkrYhZ4XFMXfJoNyB8JEpvkCQPNLZRfuhQaSsSurHrMqVKwHvbpD3wHQFTa5U3SBDDPHRhDLmkYfu59Upee8kVSLX8VeKXz4xhBa7z"
exchange_xprivate_key = "tprv8ZgxMBicQKsPdnKjmf8nZmUBfoQp35CTmFptdBNH2beX1obbD6WM7Ryx2vFTMoYxSvWYRHzJ6cKKwTFZ5r7TYGmFiwZp2f6dmavRCf7vAXo"


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


def generate_new_tree(network):
    seed = wallet.generate_mnemonic()
    w = wallet.create_wallet(network=network, seed=seed, children=1)
    return {'mnemonic': seed, 'xprivate_key': w['xprivate_key'], 'xpublic_key': w['xpublic_key']}

if __name__ == '__main__':
    print(create_address('QTUMTEST', 'tpubD6NzVbkrYhZ4YJJMroCyRuDhQMF4uqn7p2aZYk4i3KPh86dHd7Cgm3TdQ4oCPftH8TdVZ4dHYRKCvLujDCwoamKadFmU4MGqAKZVueiVEvR', 0))
    #print(create_private_key('QTUM', 'xprv9s21ZrQH143K41ZUuj7bpxQyjxyx9j7jRCdQLdamksvVNN5NSEj2hxnoKmjGFcSY6k3TyXZo78s7bXE4Jf38bXysgyPoE2qTx5fcowFQviv', 0))
    #print(generate_new_tree('BTCTEST'))
