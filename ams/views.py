# Builtins
import json
import time
import logging
import datetime
import string
from random import choice
from hashlib import sha256

#Third-party
import tornado.web
from tornado import gen
import tornado_components.web 


# Locals
from . import models
import settings
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum



class AMSHandler(tornado_components.web.ManagementSystemHandler):
	"""Account Management System Handler
	"""
	def initialize(self, client_storage, client_balance, client_email):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email 


	def double_sha256(self, str):
		"""Creating entropy with double sha256
		"""
		return sha256(sha256(str).digest()).hexdigest()


	def generate_token(self, length=16, chars=string.ascii_letters + string.punctuation + string.digits):
		return "".join(choice(chars) for x in range(0, length))

	
	async def post(self):
		"""Create new account
		"""

		# Include sign-verify mechanism
		super().verify()

		# Save data at storage database
		data = { k: self.get_argument(k) for k in self.request.arguments}
		new_account = await models.create_account(self.client_storage, data)
	
		if "error" in new_account.keys():
			# Raise error if the one does exist
			self.set_status(new_account["error"])
			self.write(new_account)
			raise tornado.web.Finish

		# Create wallet
		#entropy = self.double_sha256(public_key.encode())
		entropy = self.generate_token()
		qtum = Qtum(entropy, mainnet=False)
		address = qtum.get_qtum_address()

		# Write wallet to database
		wallet = Qtum.public_key_to_hex_address(data["public_key"])
		walletdata = {
			"public_key":data["public_key"],
			"wallet": wallet
		}
		self.client_storage.request(method_name="createwallet", **walletdata)

		# Send wallet to balance server
		balance_params = {
			"coinid": "qtum",
			"uid": new_account["id"],
			"address": address}
		new_addr = await self.client_balance.request(method_name="addaddr", 
													**balance_params)

		# Receive balance from balance host
		request_balance = {
			"uid": new_account["id"]
		}
		balance = await self.client_balance.request(method_name="getbalance", 
													**request_balance)
		logging.debug("[+] -- Balance debugging")
		logging.debug(balance)
		balance_as_digit = int(balance[str(new_account["id"])])
		#Prepare response 
		new_account.update({"href": settings.ENDPOINTS["ams"]+"/"+ new_account["public_key"],
							"balance": balance_as_digit,
							"address":address})
		# Send mail to user
		email_data = {
			"to": new_account["email"],
        	"subject": "Robin8 Support",
         	"optional": "Your account was created on %s" % settings.host + new_account["href"]
        }
		#self.client_email.request(method_name="sendmail", **email_data)

		self.write(new_account)
		

class AccountHandler(tornado_components.web.ManagementSystemHandler):

	def initialize(self, client_storage, client_balance, client_email):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		super().verify()
		# Get id from database
		response = await self.client_storage.request(method_name="getaccountdata",
												public_key=public_key)
		try:
			error_code = response["error"]
		except:
			# Receive balance from balance host
			balance = await self.client_balance.request(method_name="getbalance", 
														 uid=response["id"])
			balance_as_digit = int(balance[str(response["id"])])
			# Prepare response
			response.update({"balance":balance_as_digit})
			# Return account data
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(response)
			raise tornado.web.Finish



class NewsHandler(tornado_components.web.ManagementSystemHandler):

	def initialize(self, client_storage, client_balance, client_email):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		super().verify()

		response = await self.client_storage.request(method_name="getnews", 
												public_key=public_key)
		# If we`ve got a empty or list with news 
		if isinstance(response, list):
			self.write(json.dumps(response))
			raise tornado.web.Finish
		# If we`ve got a message with error
		elif isinstance(response, dict):
			try:
				error_code = response["error"]
			except:
				self.write(response)
			else:
				self.set_status(error_code)
				self.write(response)
				raise tornado.web.Finish

