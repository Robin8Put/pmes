import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from robin8.qrc20_sc import Qrc20

available_coinid = ["BTCTEST", "LTCTEST"]
hosts = {
	"BTCTEST": "http://%s:%s@%s:%s" % ("bitcoin", "bitcoin123", "190.2.148.11", "50011"),
	"LTCTEST": "http://%s:%s@%s:%s" % ("litecoin", "litecoin123", "190.2.148.11", "50012"),
	"QTUMTEST": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013"),
	"PUTTEST": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013")
}


if __name__ == '__main__':
    abi = '[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"},{"name":"extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'

    put_address = 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4'
    handler = Qrc20.from_http_provider("http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013"), put_address, abi)
    handler.set_send_params({'sender': 'qPszipAbyhFELfkoFbsnmVu3tSkXVNm9tQ'})
    result = handler.transfer('D1F2279EA48FFFD48679BC914A8CD7066AA3584E', 100000000)
    print(result)