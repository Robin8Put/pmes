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
	def initialize(self, storagehost, balancehost):
		self.storage = storagehost
		self.balance = balancehost

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
		super().verify()

		# Save data at storage database
		data = { k: self.get_argument(k) for k in self.request.arguments}
		new_account = models.create(self.storage, data)
		logging.debug("[+] -- Start AMS handler")
		try:
			error_code = new_account["error"]
			error_reason = new_account["reason"]
		except:
			# Create wallet
			#entropy = self.double_sha256(public_key.encode())
			entropy = self.generate_token()
			qtum = Qtum(entropy)
			address = qtum.get_qtum_address()
			# Send wallet to balance server
			balance_params = {
				"coinid": "qtum",
				"uid": new_account["id"],
				"address": address}
			client = HTTPClient(self.balance)
			client.request(method_name="addaddr", **balance_params)

			# Receive balance from balance host
			request_balance = {
				"uid": new_account["id"]
			}
			balance = client.request(method_name="getbalance", **request_balance)

			#Prepare response 
			new_account.update({"href": settings.ENDPOINTS["ams"]+"/"+ new_account["public_key"],
								"balance": balance[address],
								"address":address})

			self.write(new_account)
		else:
			# Raise error if the one does exist
			self.set_status(error_code)
			self.write(new_account)
			raise tornado.web.Finish


class AccountHandler(tornado_components.web.ManagementSystemHandler):

	def initialize(self, storagehost, balancehost):
		self.storage = storagehost
		self.balance = balancehost

	def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		super().verify(public_key)
		# Get id from database
		client = HTTPClient(self.storage)
		#request = requests.get(self.storage, params={"public_key": public_key})
		response = client.request(method_name="getaccountdata",
									public_key=public_key)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Receive balance from balance host
			request_balance = {
				"uid": response["id"]
			}
			client = HTTPClient(self.balance)
			balance = client.request(method_name="getbalance", **request_balance)
			# Prepare response
			response.update({"balance":balance})
			# Return account data
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(response)
			raise tornado.web.Finish



class BalanceHandler(tornado_components.web.ManagementSystemHandler):

	def initialize(self, storagehost, balancehost):
		self.storage = storagehost
		self.balance = balancehost

	def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		super().verify()
		# Get id from database
		######################
		client = HTTPClient(self.storage)
		response = client.request(method_name="getaccountdata",
								  **{"public_key":public_key})
		
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Receive balance from balance host
			###################################
			request_balance = {
				"uid": response["id"]
			}
			client = HTTPClient(self.balance)
			balance = client.request(method_name="getbalance", **request_balance)

			self.write(balance)
		else:
			self.set_status(error_code)
			self.write(response)
			raise tornado.web.Finish


class NewsHandler(tornado_components.web.ManagementSystemHandler):
	"""GET/POST news for users account
	"""
	def initialize(self, storagehost, balancehost):
		self.storage = storagehost
		self.balance = balancehost

	def get(self, public_key):
		"""Receives public key and returns news for users account.
		"""
		super().verify()
		data = {k: self.get_argument(k) for k in self.request.arguments}
		request_news = {
				"public_key": public_key
			}
	
		response = RPCClient.getrecentnews(self.storage, request_news)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			self.write({"news":response})
		else:
			self.set_status(error_code)
			self.write(response)
			raise tornado.web.Finish



			


