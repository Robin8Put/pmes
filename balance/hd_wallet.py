from pywallet import wallet
from pywallet.wallet import get_network
from pywallet.utils import (
    Wallet, HDPrivateKey, HDKey
)
import settings


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
        "coinid": network,
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


def extend_tree(xpublic_key, available_coins, rng):
    res = []
    for i in rng:
        for coinid in available_coins:
            entry = create_address(coinid, xpublic_key, i)
            entry.update(
                {'amount_active': 0, 'amount_frozen': 0}
            )
            res.append(entry)
    return res

def extend_database(xpublic_key, available_coins, rng, db):
    for i in rng:
        for coinid in available_coins:
            collection = db[coinid]
            entry = create_address(coinid, xpublic_key, i)
            entry.update(
                {'amount_active': 0, 'amount_frozen': 0}
            )
            print(entry)
            collection.insert_one(entry)

def generate_new_tree(network):
    seed = wallet.generate_mnemonic()
    w = wallet.create_wallet(network=network, seed=seed, children=1)
    return {'mnemonic': seed, 'xprivate_key': w['xprivate_key'], 'xpublic_key': w['xpublic_key']}

if __name__ == '__main__':
    xpublic_key = 'xpub661MyMwAqRbcFrh1bAM1a5bY4QMqPCYTduUuUb9gHhbnAzkahY9T5sqjc21FCVwDnDFQ9xauWBaeREK2k1FcN85HJhSVchCtgmQSbM7Y2pb'
    available_coins = ['QTUM', 'PUT']
    rng = range(1, 100)
    client = settings.SYNC_DB_CLIENT
    database = client[settings.BALANCE]
    extend_database(xpublic_key, available_coins, rng, database)
