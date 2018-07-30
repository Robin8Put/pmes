from bitcoinrpc.authproxy import AuthServiceProxy
from scripts.hd_wallet import create_private_key, exchange_xprivate_key, exchange_xpublic_key, available_coins, \
    create_address

if __name__ == '__main__':
    ltc_host = "http://%s:%s@%s:%s" % ("litecoinuser", "litecoin2018", "pdms2.robin8.io", "51337")
    btc_host = "http://%s:%s@%s:%s" % ("bitcoinuser", "bitcoin2018", "pdms2.robin8.io", "51338")

    connections = {
        'BTCTEST': AuthServiceProxy(btc_host),
        'LTCTEST': AuthServiceProxy(ltc_host)
    }

    btc = connections['BTCTEST']
    ltc = connections['LTCTEST']

    #print(btc.help())
    #print(btc.getbalance('mmqZrqV1b55LymW22psvQNSyDuS33t6FbT'))
    #print(ltc.getbalance('mmqZrqV1b55LymW22psvQNSyDuS33t6FbT'))
    print(ltc.listunspent())
    print(btc.listunspent())

    print(btc.sendtoaddress("mzf3cMX48ZofXj4AgGFudgWMhnz29965mV", "0.1"))

    #print(ltc.dumpprivkey('mmqZrqV1b55LymW22psvQNSyDuS33t6FbT'))
    # for i in range(0, 1):
    #   for type in available_coins:
    #       key = create_private_key(network=type, xprv=exchange_xprivate_key, uid=i)
    #       if key['type'] in connections:
    #           try:
    #               #connections[key['type']].importprivkey(key['private_key'])
    #               print(key['private_key'])
    #           except:
    #               pass