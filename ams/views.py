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
import settings
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum


class BalanceHandler(tornado.web.RequestHandler):

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


	def initialize(self, client_storage, client_balance, client_email):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, uid):

		balance = await self.client_balance.request(method_name="getbalance",
												uid=uid)
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish

		self.write(balance)


	async def post(self, uid):
		body = json.loads(self.request.body)
		amount = body.get("amount")
		balance = await self.client_balance.request(method_name="incbalance",
												uid=uid, amount=amount)
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish

		self.write(balance)

	def options(self, uid):
		self.write(json.dumps(["GET", "POST"]))


class AMSHandler(tornado_components.web.ManagementSystemHandler):
	"""Account Management System Handler
	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

	def initialize(self, client_storage, client_balance, client_email):
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email 


	async def double_sha256(self, str):
		"""Creating entropy with double sha256
		"""
		return sha256(sha256(str).digest()).hexdigest()


	async def generate_token(self, length=16, chars=string.ascii_letters + string.punctuation + string.digits):
		return "".join(choice(chars) for x in range(0, length))

	
	async def post(self):
		"""Create new account
		"""

		# Include sign-verify mechanism
		super().verify()

		# Save data at storage database
		data = json.loads(self.request.body)
		new_account = await self.client_storage.request(method_name="createaccount",
															**data)
		if "error" in new_account.keys():
			# Raise error if the one does exist
			self.set_status(new_account["error"])
			self.write(new_account)
			raise tornado.web.Finish

		# Create wallet
		#entropy = await self.double_sha256(public_key.encode())
		entropy = await self.generate_token()
		qtum = Qtum(entropy, mainnet=False)
		address = qtum.get_qtum_address()

		# Write wallet to database
		wallet = Qtum.public_key_to_hex_address(data["public_key"])
		walletdata = {
			"public_key":data["public_key"],
			"wallet": wallet
		}
		await self.client_storage.request(method_name="createwallet", **walletdata)

		# Send wallet to balance server
		balance_params = {
			"coinid": "qtum",
			"uid": new_account["id"],
			"address": address}
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
		balance = await self.client_balance.request(method_name="getbalance", 
													**request_balance)
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish

		balance_as_digit = list(balance.values())[0]
		#Prepare response 
		new_account.update({"href": settings.ENDPOINTS["ams"]+"/"+ new_account["public_key"],
							"balance": balance_as_digit,
							"address":address})
		# Send mail to user
		if new_account.get("email"):
			email_data = {
				"to": new_account["email"],
	        	"subject": "Robin8 Support",
	         	"optional": "Your account was created on %s" % settings.domain + new_account["href"]
	        }
			await self.client_email.request(method_name="sendmail", **email_data)

		self.write(new_account)

	def options(self):
		self.write(json.dumps(["POST"]))



class AccountHandler(tornado_components.web.ManagementSystemHandler):

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


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
		if "error" in response.keys():
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

			# Receive balance from balance host
		balance = await self.client_balance.request(method_name="getbalance", 
													 uid=response["id"])
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish
	
		# Prepare response
		response.update({"balance":list(balance.values())[0]})
		response.update({"address":list(balance.keys())[0]})
		# Return account data
		self.write(response)

	def options(self, public_key):
		self.write(json.dumps(["GET"]))



class NewsHandler(tornado_components.web.ManagementSystemHandler):


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


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

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class OutputOffersHandler(tornado_components.web.ManagementSystemHandler):
	"""Allows to retrieve all users output offers. 
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
	

	def initialize(self, client_storage, client_balance, client_email):
		"""Initializes:
		- client for storage requests
		- client for balance requests
		- client for email requests
		"""
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, public_key):
		"""Retrieves all users input and output offers
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		super().verify()

		account = await self.client_storage.request(method_name="getaccountdata",
												public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)

		offers = await self.client_storage.request(method_name="getoffers", 
												public_key=public_key)
		if isinstance(offers, dict):
			self.set_status(offers["error"])
			self.write(offers)
			raise tornado.web.Finish

		self.write(json.dumps(offers))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class InputOffersHandler(tornado_components.web.ManagementSystemHandler):
	"""Allows to retrieve all users output offers. 
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
	

	def initialize(self, client_storage, client_balance, client_email):
		"""Initializes:
		- client for storage requests
		- client for balance requests
		- client for email requests
		"""
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, public_key):
		"""Retrieves all users input and output offers
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		super().verify()
		message = json.loads(self.get_argument("message"))
		cid = message.get("cid")
		if not cid:
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields."})

		account = await self.client_storage.request(method_name="getaccountdata",
												public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)

		offers = await self.client_storage.request(method_name="getoffers", 
												public_key=public_key, cid=cid)
		if isinstance(offers, dict):
			self.set_status(offers["error"])
			self.write(offers)
			raise tornado.web.Finish

		self.write(json.dumps(offers))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class ContentsHandler(tornado_components.web.ManagementSystemHandler):
	"""Allows to retrieve all users contents
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

	def initialize(self, client_storage, client_balance, client_email):
		"""Initializes:
		- client for storage requests
		- client for balance requests
		- client for email requests
		"""
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	async def get(self, public_key):
		"""Retrieves all users contents
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		super().verify()
		contents = await self.client_storage.request(method_name="getuserscontent",
														public_key=public_key)
		if isinstance(contents, dict):
			self.set_status(contents["error"])
			self.write(contents)
			raise tornado.web.Finish

		self.write(json.dumps(contents))


	def options(self):
		self.write(json.dumps(["GET"]))










