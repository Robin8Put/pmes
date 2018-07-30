# Built-ins
import os
import json
import logging

# Third-party
from jsonrpcserver.aio import methods
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from robin8.qrc20_sc import Qrc20

# todo: move to global settings
available_coinid = ["BTCTEST", "LTCTEST", "PUTTEST", "QTUMTEST"]
hosts = {
	"BTCTEST": "http://%s:%s@%s:%s" % ("bitcoin", "bitcoin123", "190.2.148.11", "50011"),
	"LTCTEST": "http://%s:%s@%s:%s" % ("litecoin", "litecoin123", "190.2.148.11", "50012"),
	"QTUMTEST": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013"),
	"PUTTEST": "http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013")
}
decimals = 8
decimals_k = 10**decimals


class AbstractWithdraw(object):

	def __init__(self):
		self.reload_connections()

	def reload_connections(self):
		self.connections = {}
		for coinid in available_coinid:
			self.connections.update({coinid: AuthServiceProxy(hosts[coinid])})

	def error_403(self, reason):
		return {"error": 403, "reason":"Withdraw service. " + reason}

	def error_400(self, reason):
		return {"error": 400, "reason":"Withdraw service. " + reason}

	def error_404(self, reason):
		return {"error": 404, "reason":"Withdraw service. " + reason}


	def validate(self, *args, **kwargs):

		if not kwargs:
			self.error_400("Validate. Missed parameters.")
			return

		message = kwargs.get("message")

		if message and isinstance(message, str):
			kwargs = json.loads(message)
		elif message and isinstance(message, dict):
			kwargs = message

		amount = kwargs.get("amount")
		if amount and not isinstance(amount, int):
			self.error_400("Validate. Not valid amount")
			return

		coinid = kwargs.get("coinid")
		if coinid not in available_coinid:
			self.error_403("Validate. Not valid coinid")


class Withdraw(AbstractWithdraw):


	async def withdraw(self, *args, **kwargs):
		"""
		Withdraw funds to user wallet

		Accepts:
			- coinid [string] (blockchain id (example: BTCTEST, LTCTEST))
			- address [string] withdrawal address
			- amount [int]     withdrawal amount multiplied by decimals_k (10**8)
		Returns dictionary with following fields:
			- txid [string]
		"""

		super().validate(*args, **kwargs)
		super().reload_connections()


		coinid = kwargs.get("coinid")
		address = kwargs.get("address")
		amount = int(kwargs.get("amount"))

		connection = self.connections[coinid]

		if coinid in ['BTCTEST', 'LTCTEST', 'QTUMTEST']:
			try:
				txid = connection.sendtoaddress(address, str(amount/decimals_k))
				return {"txid": txid}
			except Exception as e:
				return {"error": 400, "reason": str(e)}
		elif coinid == 'PUTTEST':
			abi = '[{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"from","type":"address"},{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"who","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"value","type":"uint256"},{"name":"extraData","type":"bytes"}],"name":"approveAndCall","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'

			put_address = 'b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4'
			handler = Qrc20.from_http_provider(
					"http://%s:%s@%s:%s" % ("qtum", "qtum123", "190.2.148.11", "50013"),
						put_address, abi)
			handler.set_send_params({'sender': 'qPszipAbyhFELfkoFbsnmVu3tSkXVNm9tQ'})
			try:
				txid = handler.transfer(address, amount)['txid']
				return {'txid': txid}
			except Exception as e:
				return {"error": 400, "reason": str(e)}
				


withdraw2 = Withdraw()


@methods.add
async def withdraw(*args, **kwargs):
	request = await withdraw2.withdraw(*args, **kwargs)
	return request