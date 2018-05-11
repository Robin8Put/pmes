# Builtins
import json
import time
import logging
import datetime
import string
from random import choice
from hashlib import sha256

#Third-party
from jsonrpcserver import dispatch
import tornado.web
import tornado_components.web 
import tornado_components.mongo
from jsonrpcclient.http_client import HTTPClient
from jsonrpcserver.aio import methods
import requests

# Locals
from . import models
import settings
from tornado_components.rpc_client import RPCClient
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum



class AMSHandler(tornado_components.web.ManagementSystemHandler):
	"""Account Management System Handler
	"""

	def double_sha256(self, str):
		"""Creating entropy with double sha256
		"""
		return sha256(sha256(str).digest()).hexdigest()


	def generate_token(self, length=16, chars=string.ascii_letters + string.punctuation + string.digits):
		return "".join(choice(chars) for x in range(0, length))


	def post(self):
		"""Create new account
		"""

		# Include sign-verify mechanism
		super().post()

		# Save data at storage database
		data = { k: self.get_argument(k) for k in self.request.arguments}
		storage_url = "%s:%s" % (settings.host, settings.storageport) 
		new_account = models.create(storage_url, data)
		try:
			error_code = new_account["error"]
			error_reason = new_account["reason"]
		except:
			# Create wallet
			#entropy = self.double_sha256(public_key.encode())
			entropy = self.generate_token()
			qtum = Qtum(entropy)
			address = qtum.get_qtum_address()
			# Send waalet to balance server
			balance_params = {
				"coinid": "qtum",
				"uid": new_account["id"],
				"address": address}
			balance_host = "%s:%s" % (settings.host,settings.balanceport)
			client = HTTPClient(balance_host)
			client.request(method_name="addaddr", **balance_params)

			# Receive balance from balance host
			request_balance = {
				"uid": new_account["id"]
			}
			balance = client.request(method_name="getbalance", **request_balance)

			#Prepare response 
			new_account.update({"href": "/api/" + new_account["public_key"],
								"balance": balance[address],
								"address":address})

			self.write(new_account)
		else:
			# Raise error if the one does exist
			raise tornado.web.HTTPError(error_code, error_reason)


class AccountHandler(tornado_components.web.ManagementSystemHandler):

	def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		# Get id from database
		storage_url = "%s:%s" % (settings.host, settings.storageport)
		request = requests.get(storage_url, params={"public_key": public_key})
		
		try:
			error_code = request.json()["error"]
			error_reason = request.json()["reason"]
		except:
			# Receive balance from balance host
			request_balance = {
				"uid": request.json()["id"]
			}
			balance_host = "%s:%s" % (settings.host,settings.balanceport)
			client = HTTPClient(balance_host)
			balance = client.request(method_name="getbalance", **request_balance)
			# Prepare response
			response = request.json()
			response.update({"balance":balance})
			# Return account data
			self.write(response)
		else:
			raise tornado.web.HTTPError(error_code, error_reason)


		


class BalanceHandler(tornado_components.web.ManagementSystemHandler):

	def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		# Get id from database
		######################
		storage_url = "%s:%s" % (settings.host, settings.storageport)
		request = requests.get(storage_url, params={"public_key": public_key})
		
		try:
			error_code = request.json()["error"]
			error_reason = request.json()["reason"]
		except:
			# Receive balance from balance host
			###################################
			request_balance = {
				"uid": request.json()["id"]
			}
			balance_host = "%s:%s" % (settings.host,settings.balanceport)
			client = HTTPClient(balance_host)
			balance = client.request(method_name="getbalance", **request_balance)

			self.write(balance)
		else:
			raise tornado.web.HTTPError(error_code, error_reason)

