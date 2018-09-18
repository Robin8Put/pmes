mainnet = True

with open('./keys/ecprivkey.pem') as f:
    private_key = f.read()

with open('./keys/ecpubkey.pem') as f:
    public_key = f.read()

check_sig = False

deploy_settings = {
    'QTUMTEST': {
        'gasLimit': 2500000,
        'gasPrice': 490000000000
    },
    'QTUM': {
        'gasLimit': 2500000,
        'gasPrice': 490000000000
    },
    'ETHRINKEBY': {
        'gasLimit': 2500000,
        'gasPrice': 4900000000
    },
    'ETH': {
        'gasLimit': 2500000,
        'gasPrice': 7900000000
    }
}

transfer_settings = {
    'QTUMTEST': {
        'gasLimit': 500000,
        'gasPrice': 490000000000
    },
    'QTUM': {
        'gasLimit': 500000,
        'gasPrice': 490000000000
    },
    'ETHRINKEBY': {
        'gasLimit': 250000,
        'gasPrice': 4900000000
    },
    'ETH': {
        'gasLimit': 2500000,
        'gasPrice': 7900000000
    }
}

base_blockchains = ['QTUMTEST', 'ETHRINKEBY',
                    'QTUM', 'ETH']  # supported blockchains to create custom tokens
bitcoinlike_coinids = ["BTCTEST", "LTCTEST", "QTUMTEST", "PUTTEST",
                       'BTC', 'LTC', 'QTUM', 'PUT']
ethereumlike_coinids = ["ETHRINKEBY", 'KTOKENRINKEBY', 'OMGRINKEBY', 'REPRINKEBY',
                        'ETH', 'KTOKEN', 'OMG', 'REP']

ethereum_tokens = ['KTOKENRINKEBY', 'OMGRINKEBY', 'REPRINKEBY', 'KTOKEN', 'OMG', 'REP']
qtum_tokens = ['PUTTEST', 'PUT']

testnet_hosts = {
    "BTCTEST": "http://%s:%s@%s:%s" % ("bitcoin", "bitcoin123", "190.2.148.11", "50011"),
    "LTCTEST": "http://%s:%s@%s:%s" % ("litecoin", "litecoin123", "190.2.148.11", "50012"),
    "QTUMTEST": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013"),

    "PUTTEST": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013"),

    "ETHRINKEBY": "http://%s:%s" % ("190.2.148.11", "50014"),

    'KTOKENRINKEBY': "http://%s:%s" % ("190.2.148.11", "50014"),
    'OMGRINKEBY': "http://%s:%s" % ("190.2.148.11", "50014"),
    'REPRINKEBY': "http://%s:%s" % ("190.2.148.11", "50014"),
}
mainnet_hosts = {
    "BTC": "http://%s:%s@%s:%s" % ("bitcoin", "bitcoin123", "190.2.148.12", "50011"),
    "LTC": "http://%s:%s@%s:%s" % ("litecoin", "litecoin123", "190.2.148.12", "50012"),
    "QTUM": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.12", "50013"),

    "PUT": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.12", "50013"),

    "ETH": "http://%s:%s" % ("190.2.148.12", "50014"),

    'KTOKEN': "http://%s:%s" % ("190.2.148.12", "50014"),
    'OMG': "http://%s:%s" % ("190.2.148.12", "50014"),
    'REP': "http://%s:%s" % ("190.2.148.12", "50014"),
}

hosts = {}
hosts.update(testnet_hosts)
if mainnet:
    hosts.update(mainnet_hosts)

erc20_abi = '[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"},{"name":"extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'

contract_addresses = {
    'PUTTEST': 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4',

    'KTOKENRINKEBY': '0x0f54d6c9373630c456fb5320545eA0bbbD0e8347',
    'OMGRINKEBY': '0x55aE4DDF1F2b69535439aD461CD4C0F3c5116Fc7',
    'REPRINKEBY': '0x6A732d537DAf79d75EFaeAE286D30FC578Fa98D0',

    'PUT': '4060e21ac01b5c5d2a3f01cecd7cbf820f50be95',

    'OMG': '0xd26114cd6EE289AccF82350c8d8487fedB8A0C07',
    'REP': '0xe94327d07fc17907b4db788e5adf2ed424addff6'
}

hot_wallets = {
    'QTUMTEST': 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis',
    'ETHRINKEBY': '0xa82E57390cEbdbBE56AB408Dc967EA068216dc19',
    'BTCTEST': 'mmqZrqV1b55LymW22psvQNSyDuS33t6FbT',
    'LTCTEST': 'mmqZrqV1b55LymW22psvQNSyDuS33t6FbT',

    'PUTTEST': 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis',

    'KTOKENRINKEBY': '0xa82E57390cEbdbBE56AB408Dc967EA068216dc19',
    'OMGRINKEBY': '0xa82E57390cEbdbBE56AB408Dc967EA068216dc19',
    'REPRINKEBY': '0xa82E57390cEbdbBE56AB408Dc967EA068216dc19',

    # Mainnet
    'QTUM': 'QeRPVfQVDRngpQZDEkaKVJb3QRFNyU515E',
    'ETH': '0xD306F2ab21a995EAa6424DC6885E0c6511bd1CBb',
    'BTC': '1JpQPN7n2xusPGUBpRFqN2oQuAJfhBMKB6',
    'LTC': 'Ld3MeaRc7d9ve5ALzZF8e3sB7Nfwpg6dzD',

    'PUT': 'QeRPVfQVDRngpQZDEkaKVJb3QRFNyU515E',

    'KTOKEN': '0xD306F2ab21a995EAa6424DC6885E0c6511bd1CBb',
    'OMG': '0xD306F2ab21a995EAa6424DC6885E0c6511bd1CBb',
    'REP': '0xD306F2ab21a995EAa6424DC6885E0c6511bd1CBb',
}

cold_wallets = {
    'QTUMTEST': 'qadDZDQoizArPgoiaaZE8HQXf9CCvnA7Qk',
    'ETHRINKEBY': '0x1e75d45856629CE91EbDEcf3606aF74a402c85B5',
    'BTCTEST': 'mxanhEjDLMzy2nYwMoZMm9xSzbsiU2HQ4P',
    'LTCTEST': 'mxanhEjDLMzy2nYwMoZMm9xSzbsiU2HQ4P',

    'PUTTEST': 'qadDZDQoizArPgoiaaZE8HQXf9CCvnA7Qk',

    'KTOKENRINKEBY': '0x1e75d45856629CE91EbDEcf3606aF74a402c85B5',
    'OMGRINKEBY': '0x1e75d45856629CE91EbDEcf3606aF74a402c85B5',
    'REPRINKEBY': '0x1e75d45856629CE91EbDEcf3606aF74a402c85B5',

    # Mainnet
    'QTUM': 'QPjthx2L6B4GYead9fKKzCfe1A1TaitTq2',
    'ETH': '0xa1847389F4EC5F1F0BB4a4735647034d102AD00D',
    'BTC': '148ubejcuiBT7WVbjKzqrvt1Vu4kK43Xk5',
    'LTC': 'LNMrrs3SzNRWNKBkuTz98wwmi7S2UTG7BL',

    'PUT': 'QPjthx2L6B4GYead9fKKzCfe1A1TaitTq2',

    'KTOKEN': '0xa1847389F4EC5F1F0BB4a4735647034d102AD00D',
    'OMG': '0xa1847389F4EC5F1F0BB4a4735647034d102AD00D',
    'REP': '0xa1847389F4EC5F1F0BB4a4735647034d102AD00D',
}
eth_passphrase = 'eth2018'

decimals = 8
decimals_k = 10 ** decimals

with open('contract_templates/erc20.sol') as erc_file:
    erc20_code = erc_file.read()

WITHDRAW_DELAY = 120000
OUTPUTS_PER_TX = 50
