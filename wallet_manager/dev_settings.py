from pywallet import network

networks = {
    'BTCTEST': network.BitcoinTestNet,
    'LTCTEST': network.LitecoinTestNet,
    'QTUMTEST': network.QtumTestNet,

    'BTC': network.BitcoinMainNet,
    'LTC': network.LitecoinMainNet,
    'QTUM': network.QtumMainNet
}
