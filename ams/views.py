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


# Locals
import settings
from utils.tornado_components import web 
from utils.tornado_components.timestamp import get_time_stamp
from utils.qtum_utils.qtum import Qtum
from utils.bip32keys.r8_ethereum.r8_eth import R8_Ethereum #public_key_to_checksum_address 

validator = {
		"QTUM": lambda x: Qtum.public_key_to_hex_address(x),
		"ETH": lambda x: R8_Ethereum.public_key_to_checksum_address(x)
}

ident_offer = {0:"read_access", 1:"write_access"}



class BalanceHandler(tornado.web.RequestHandler):
	"""This is a class for test funds (emulating increment account )

	It has to be removed before production
	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email
		self.client_bridge = client_bridge



	async def get(self, uid):

		balance = await self.client_balance.request(method_name="getbalance",
												uid=uid)
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish

		self.write(balance)


	async def post(self, uid):
		try:
			data = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
			
		amount = data.get("amount")
		coinid  =data.get("coinid")
		balance = await self.client_balance.request(method_name="incbalance",
										uid=uid, amount=amount, coinid=coinid)
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish

		self.write(balance)

	def options(self, uid):
		self.write(json.dumps(["GET", "POST"]))


class AMSHandler(web.ManagementSystemHandler):
	""" Handles creating account requests

	Endpoint: /api/accounts

	Allowed methods: POST

	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email 
		self.client_bridge = client_bridge


	
	async def post(self):
		"""Creates new account

		Accepts:
			- message (signed dict):
				- "device_id" - str
				- "email" - str
				- "phone" - str
			- "public_key" - str
			- "signature" - str

		Returns:
			dictionary with following fields:
				- "device_id" - str
				- "phone" - str
				- "public_key" - str
				- "count" - int  ( wallets amount )
				- "level" - int (2 by default)
				- "news_count" - int (0 by default)
				- "email" - str
				- "href" - str
				- "wallets" - list

		Verified: True

		"""

		# Include signature verification mechanism
		super().verify()

		# Save data at storage database
		try:
			data = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
		message = data["message"]

		# Create account
		new_account = await self.client_storage.request(method_name="createaccount",
															**data)
		if "error" in new_account.keys():
			# Raise error if the one does exist
			self.set_status(new_account["error"])
			self.write(new_account)
			raise tornado.web.Finish

		# Create new wallets for account
		balance_params = {
			"uid": new_account["id"]
		}
		new_addr = await self.client_balance.request(method_name="addaddr", 
													**balance_params)
		if "error" in new_addr.keys():
			self.set_status(new_addr["error"])
			self.write(new_addr)
			raise tornado.web.Finish

		# Receive balance from balance host
		request_balance = {
			"uid": new_account["id"]
		}
		wallets = await self.client_balance.request(method_name="getbalance", 
													**request_balance)
		if isinstance(wallets, dict):
			if "error" in wallets.keys():
				self.set_status(wallets["error"])
				self.write(wallets)
				raise tornado.web.Finish

		#Prepare response 
		new_account.update({"href": settings.ENDPOINTS["ams"]+"/"+ new_account["public_key"],
							"wallets": json.dumps(wallets)})
		# Send mail to user
		if new_account.get("email"):
			email_data = {
				"to": new_account["email"],
	        	"subject": "Robin8 Support",
	         	"optional": "Your account was created on %s" % settings.domain + new_account["href"]
	        }
			await self.client_email.request(method_name="sendmail", **email_data)
		# Response
		self.write(new_account)


	def options(self):
		self.write(json.dumps(["POST"]))



class AccountHandler(web.ManagementSystemHandler):
	""" Receive account data

	Endpoint: /api/accounts/[public_key]

	Allowed methods: GET

	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email
		self.client_bridge = client_bridge



	async def get(self, public_key):
		""" Receive account data

		Accepts:
			Query string:
				- "public_key" - str
			Query string params:
				- message ( signed dictionary ):
					- "timestamp" - str
	
		Returns:
				- "device_id" - str
				- "phone" - str
				- "public_key" - str
				- "count" - int  ( wallets amount )
				- "level" - int (2 by default)
				- "news_count" - int (0 by default)
				- "email" - str
				- "wallets" - list
		
		Verified: True

		"""
		# Signature verification
		super().verify()

		# Get account
		response = await self.client_storage.request(method_name="getaccountdata",
												public_key=public_key)
		if "error" in response.keys():
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		# Receive balances from balance host
		wallets = await self.client_balance.request(method_name="getbalance", 
													 uid=response["id"])
		if isinstance(wallets, dict):
			if "error" in wallets.keys():
				self.set_status(wallets["error"])
				self.write(wallets)
				raise tornado.web.Finish
		
		# Prepare response
		response.update({"wallets":json.dumps(wallets)})
		# Return account data
		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["GET"]))



class NewsHandler(web.ManagementSystemHandler):


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email
		self.client_bridge = client_bridge



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
				del response["account_id"]

				self.write(response)
			else:
				self.set_status(error_code)
				self.write(response)
				raise tornado.web.Finish

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class OutputOffersHandler(web.ManagementSystemHandler):
	"""Allows to retrieve all users output offers. 
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
	

	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		"""Initializes:
		- client for storage requests
		- client for balance requests
		- client for email requests
		"""
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email
		self.client_bridge = client_bridge



	async def get(self, public_key):
		"""Retrieves all users input and output offers
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		super().verify()
		# Get coinid
		account = await self.client_storage.request(method_name="getaccountdata",
												public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish



		offers_collection = []
		for coinid in settings.AVAILABLE_COIN_ID:

			self.client_bridge.endpoint = settings.bridges[coinid]

			try:
				offers = await self.client_bridge.request(method_name="get_buyer_offers", 
											buyer_address=validator[coinid](public_key))
				for offer in offers:
					offer["type"] = ident_offer[offer["type"]]
	
				storage_offers = await self.client_storage.request(method_name="getoffers",
														coinid=coinid, public_key=public_key)

			except:
				continue

			offers_collection.extend(offers + storage_offers)


		self.write(json.dumps(offers_collection))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class InputOffersHandler(web.ManagementSystemHandler):
	"""Allows to retrieve all users output offers. 
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
	

	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		"""Initializes:
		- client for storage requests
		- client for balance requests
		- client for email requests
		"""
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email
		self.client_bridge = client_bridge



	async def get(self, public_key):
		"""Retrieves all users input and output offers
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		super().verify()
		message = json.loads(self.get_argument("message"))
		cid = message.get("cid")
		coinid = message.get("coinid")
		if not cid:
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields."})
			raise tornado.web.Finish


		account = await self.client_storage.request(method_name="getaccountdata",
												public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		offers = await self.client_bridge.request(method_name="get_cid_offers", cid=cid)

		if isinstance(offers, dict):
			self.set_status(offers["error"])
			self.write(offers)
			raise tornado.web.Finish

		for offer in offers:
			offer["type"] = ident_offer[offer["type"]]

		storage_offers = await self.client_storage.request(method_name="getoffers", 
															cid=cid, coinid=coinid)

		self.write(json.dumps(offers + storage_offers))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class ContentsHandler(web.ManagementSystemHandler):
	"""Allows to retrieve all users contents
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

	def initialize(self, client_storage, client_balance, client_email, client_bridge):
		"""Initializes:
		- client for storage requests
		- client for balance requests
		- client for email requests
		"""
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email
		self.client_bridge = client_bridge


	async def get(self, public_key):
		"""Retrieves all users contents
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		super().verify()

		cids = await self.client_storage.request(method_name="getuserscontent",
															public_key=public_key)
		
		if isinstance(cids, dict):
			if "error" in cids.keys():
				self.set_status(cids["error"])
				self.write(cids)
				raise tornado.web.Finish

		container = []

		for coinid in cids:

			if coinid in settings.AVAILABLE_COIN_ID:
				self.client_bridge.endpoint = settings.bridges[coinid]

				try:
					contents = await self.client_bridge.request(method_name="getuserscontent", 
																cids=json.dumps(cids[coinid]))
				except:
					continue
			container.extend(contents)

		self.write(json.dumps(container))


	def options(self, public_key):
		self.write(json.dumps(["GET"]))










