

deploy_settings = {
    'gasLimit': 2500000,
    'gasPrice': 490000000000
}

base_blockchains = ['QTUMTEST', 'ETHTEST']
hosts = {
    "BTCTEST": "http://%s:%s@%s:%s" % ("bitcoin", "bitcoin123", "190.2.148.11", "50011"),
    "LTCTEST": "http://%s:%s@%s:%s" % ("litecoin", "litecoin123", "190.2.148.11", "50012"),
    "QTUMTEST": "http://%s:%s@%s:%s" % ("qtumuser", "qtum2018", "localhost", "8333"),
    "PUTTEST": "http://%s:%s@%s:%s" % ("qtumuser", "qtum2018", "localhost", "8333")
}
erc20_abi = '[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"},{"name":"extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'

contract_addresses = {
    'PUTTEST': 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4'
}
qtum_hot_wallet = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'

decimals = 8
decimals_k = 10**decimals

with open('erc20.sol') as erc_file:
    erc20_code = erc_file.read()