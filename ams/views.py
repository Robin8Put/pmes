# Builtins
import json
import time
import logging
import datetime
import string
from random import choice
from hashlib import sha256
import re

#Third-party
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado_components import web 
from tornado_components.timestamp import get_time_stamp 
from tornado_components.web import RobustTornadoClient


# Locals
import settings
from utils.models.account import Account
from utils.pagination import Paginator



class BalanceHandler(tornado.web.RequestHandler):
	"""This is a class for test funds (emulating increment account )

	It has to be removed before production
	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


	def initialize(self):
		self.account = Account()


	async def get(self, uid):

		balance = await self.account.balance.getbalance(uid=uid)
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
		balance = await self.account.balance.add_active(uid=uid, amount=amount, 
														coinid=coinid)
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
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

	def initialize(self):
		self.account = Account()

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
		logging.debug("\n\n[+] -- Account debugging. ")
		# Include signature verification mechanism
		if settings.SIGNATURE_VERIFICATION:
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
		new_account = await self.account.createaccount(**data)
		logging.debug("\n\n [+] -- New account debugging.")
		logging.debug(new_account["id"])
		if "error" in new_account.keys():
			# Raise error if the one does exist
			self.set_status(new_account["error"])
			self.write(new_account)
			raise tornado.web.Finish

		# Receive balance from balance host
		wallets = await self.account.balance.get_wallets(uid=new_account["id"])
		if isinstance(wallets, dict):
			if "error" in wallets.keys():
				self.set_status(wallets["error"])
				self.write(wallets)
				raise tornado.web.Finish

		#Prepare response 
		new_account.update({"href": settings.ENDPOINTS["ams"]+"/"+ new_account["public_key"],
							"wallets": json.dumps(wallets["wallets"])})
		# Send mail to user
		if new_account.get("email"):
			email_data = {
				"to": new_account["email"],
	        	"subject": "Robin8 Support",
	         	"optional": "Your account was created on %s" % settings.domain + new_account["href"]
	        }
			await self.account.mailer.sendmail(**email_data)
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
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


	def initialize(self):
		self.account = Account()

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
		if settings.SIGNATURE_VERIFICATION:
			super().verify()

		# Get users request source
		compiler = re.compile(r"\((.*?)\)")
		match = compiler.search(self.request.headers.get("User-Agent"))
		try:
			source = match.group(1)
		except:
			source = None
		# Write source to database
		await self.account.logsource(public_key=public_key, source=source)

		# Get account
		logging.debug("\n\n [+] -- Get account data.")
		response = await self.account.getaccountdata(public_key=public_key)
		logging.debug("\n")
		logging.debug(response)
		logging.debug("\n")
		if "error" in response.keys():
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		# Receive balances from balance host
		wallets = await self.account.balance.get_wallets(uid=response["id"])
		if isinstance(wallets, dict):
			if "error" in wallets.keys():
				self.set_status(wallets["error"])
				self.write(wallets)
				raise tornado.web.Finish
		
		# Filter wallets
		response.update({"wallets":json.dumps(
					[i for i in wallets["wallets"] 
					if i.get("coinid") not in ["BTC", "LTC", "ETH"]])})
		# Return account data
		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["GET"]))



class NewsHandler(web.ManagementSystemHandler):


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


	def initialize(self):
		self.account = Account()


	async def get(self, public_key):
		"""Receives public key, looking up document at storage,
				sends document id to the balance server
		"""
		if settings.SIGNATURE_VERIFICATION:
			super().verify()

		response = await self.account.getnews(public_key=public_key)
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
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
	

	async def collect_offers(self):
		logging.debug("\n\n Collect offers debugging. ")

		for coinid in settings.bridges.keys():

			self.account.blockchain.setendpoint(settings.bridges[coinid])

			try:
				offers = await self.account.blockchain.getbuyeroffers( 
								buyer_address=self.account.validator[coinid](public_key))
				logging.debug(" * Offers")
				logging.debug(offers)
				for offer in offers:
					offer["type"] = self.account.ident_offer[offer["type"]]
	
				storage_offers = await self.account.getoffers(coinid=coinid, 
																public_key=public_key)
				logging.debug(" * Storage offers ")
				logging.debug(storage_offers)

			except:
				continue


	def initialize(self):
		self.account = Account()


	async def get(self, public_key):
		"""Retrieves all users input and output offers
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		#super().verify()
		# Get coinid
		account = await self.account.getaccountdata(public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish



		offers_collection = []
		for coinid in settings.AVAILABLE_COIN_ID:

			try:
				self.account.blockchain.setendpoint(settings.bridges[coinid])
			except:
				continue

			try:
				offers = await self.account.blockchain.getbuyeroffers( 
								buyer_address=self.account.validator[coinid](public_key))
				for offer in offers:
					offer["type"] = self.account.ident_offer[offer["type"]]
	
				storage_offers = await self.account.getoffers(coinid=coinid, 
																public_key=public_key)

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
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
	

	def initialize(self):
		self.account = Account()


	async def get(self, public_key):
		"""Retrieves all users input and output offers
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		if settings.SIGNATURE_VERIFICATION:
			super().verify()

		logging.debug("\n\n --  Input offers debugging")

		message = json.loads(self.get_argument("message"))
		cid = message.get("cid")
		coinid = message.get("coinid")
		if not cid:
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields."})
			raise tornado.web.Finish


		account = await self.account.getaccountdata(public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		if coinid in settings.bridges.keys():
			self.account.blockchain.setendpoint(settings.bridges[coinid])
		offers = await self.account.blockchain.getcidoffers(cid=cid)
		logging.debug("\n\n -- Offers")
		logging.debug(offers)

		if isinstance(offers, dict):
			self.set_status(offers["error"])
			self.write(offers)
			raise tornado.web.Finish

		for offer in offers:
			offer["type"] = self.account.ident_offer[offer["type"]]

		storage_offers = await self.account.getoffers(cid=cid, coinid=coinid)
		logging.debug("\n\n -- Storage offers. ")
		logging.debug(storage_offers)

		self.write(json.dumps(offers + storage_offers))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class ContentsHandler(web.ManagementSystemHandler):
	"""Allows to retrieve all users contents
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

	def initialize(self):
		self.account = Account()


	async def get(self, public_key):
		"""Retrieves all users contents
		Accepts:
		- public key
		"""
		# Sign-verifying functional
		if settings.SIGNATURE_VERIFICATION:
			super().verify()

		page = self.get_query_argument("page", 1)

		cids = await self.account.getuserscontent(public_key=public_key)

		logging.debug("\n\n Users cids")
		logging.debug(cids)
		
		if isinstance(cids, dict):
			if "error" in cids.keys():
				self.set_status(cids["error"])
				self.write(cids)
				raise tornado.web.Finish

		container = []

		for coinid in cids:

			logging.debug("\n [] -- coinid")
			logging.debug(coinid)

			#if list(cids.keys()).index(coinid) == len(cids) - 1:
			#	paginator = Paginator(coinid=coinid, page=page, 
			#		limit=(settings.LIMIT//len(cids))+(settings.LIMIT%len(cids)), cids=cids)
			#else:
			#paginator = Paginator(coinid=coinid, page=page, 
			#						limit=settings.LIMIT // len(cids), cids=cids)

			if coinid in settings.bridges.keys():
				logging.debug(" -- Coinid in ")
				logging.debug(settings.bridges.keys())
				self.account.blockchain.setendpoint(settings.bridges[coinid])

				contents = await self.account.blockchain.getuserscontent(
												cids=json.dumps(cids[coinid]))
				logging.debug("\n\n -- Contents")
				logging.debug(contents)
				if isinstance(contents, dict):
					if "error" in contents.keys():
						continue
				container.extend(contents)

				logging.debug("\n\n -- Container 1")


				logging.debug("\n\n -- Container 2")
				logging.debug(container)

		response = {
			"profiles":json.dumps(container),
			}
		try:
			response.update(paginator.get_pages())
		except:
			pass
	
		self.write(json.dumps(response))


	def options(self, public_key):
		self.write(json.dumps(["GET"]))


class WithdrawHandler(web.ManagementSystemHandler):
	"""
	"""
	def initialize(self):
		self.account = Account()

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header('Cache-Control', "no-store")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
	

	async def get(self):
		"""
		"""
		# Sign-verifying functional
		if settings.SIGNATURE_VERIFICATION:
			super().verify()

		address = self.get_query_argument("address", None)
		coinid = self.get_query_argument("coinid", None)

		#eth_token = "15QZDMQC1BB9YN5QQKMEW9MDZBBQECJ8ZH"

		#endpoints = {
		#	"QTUMTEST": f"https://testnet.qtum.org/insight-api/txs/?address={address}",
		#	"PUTTEST": f"https://testnet.qtum.org/insight-api/txs/?address={address}",
		#	"ETH": f"http://api.etherscan.io/api?\
		#					module=account&\
		#					action=txlist&\
		#					address={address}&\
		#					startblock=0&\
		#					endblock=99999999&\
		#					sort=asc&\
		#					apikey={eth_token}"
		#}

		#client = AsyncHTTPClient()

		#try:
		#	response = await client.fetch(endpoints[coinid])
		#	self.write(response.body)
		#except Exception as e:
		#	response = {"error":501, "reason":str(e)}
		#	self.write(response)

		txs = await self.account.get_transactions(address=address, coinid=coinid)
		if "error" in txs.keys():
			self.set_status(txs["error"])
			self.write(txs)
			raise tornado.web.Finish

		self.write(txs)


	async def post(self):
		"""
		Funds from account to given address.
		1. Verify signature
		2. Freeze senders amount.
		3. Request to withdraw server.
		4. Call balances sub_frozen method.

		Accepts:
			- message [dict]:
				- coinid [string]
				- amount [integer]
				- address [string]
				- timestamp [float]
				- recvWindow [float]
			- public_key
			- signature

		Returns:
			- message [dict]:
				- coinid [string]
				- amount [integer]
				- address [string]
				- timestamp [float]
				- recvWindow [float]
			- public_key
			- signature
			- txid [string]
		"""
		# Sign-verifying functional
		if settings.SIGNATURE_VERIFICATION:
			super().verify()

		logging.debug("\n\n[+] -- Withdraw debugging")
		# Get data from requests body
		data = json.loads(self.request.body)
		public_key = data.get("public_key")
		signature = data.get("signature")

		if isinstance(data.get("message"), str):
			message = json.loads(data["message"])
		elif isinstance(data.get("message"), dict):
			message = data["message"]

		# Get data from signed message
		coinid = message.get("coinid")
		amount = message.get("amount")
		address = message.get("address")
		timestamp = message.get("timestamp")
		recvWindow = message.get("recvWindow")
		# 
		if not all([coinid, amount, address, public_key, 
					signature, timestamp, recvWindow]):
			data.update({"error":400, "reason":"Missed required fields. "})
			self.set_status(400)
			self.write(data)
			raise tornado.web.Finish
		logging.debug(data)

		# Get account
		account = await self.account.getaccountdata(public_key=public_key)
		if "error" in account.keys():
			data.update(account)
			self.set_status(404)
			self.write(data)
			raise tornado.web.Finish
		logging.debug("\n                Senders account")
		logging.debug(account)


		# Request to balance and call freeze method
		fee = await self.account.withdraw_fee(coinid)

		freeze = await self.account.balance.freeze(uid=account["id"], coinid=coinid,
													amount=amount + fee)
		logging.debug("\n           Frozen balance")
		logging.debug(freeze)
		if "error" in freeze.keys():
			data.update(freeze)
			self.set_status(freeze["error"])
			self.write(data)
			raise tornado.web.Finish

		# Request to withdraw server
		txid = await self.account.withdraw(amount=amount, coinid=coinid, 
							address=address)
		logging.debug("\n      Withdraw server response")
		logging.debug(txid)

		# Check if txid exists
		if "error" in txid.keys():
			await self.account.balance.unfreeze(uid=account["id"], coinid=coinid,
														amount=amount + fee)
			data.update(txid)
			self.set_status(500)
			self.write(data)
			raise tornado.web.Finish

		# Add balance to recepient
		#add_active = await self.account.balance.add_active(address=address, coinid=coinid,
		#													amount=amount)
		#if "error" in add_active.keys():
		#	await self.account.balance.unfreeze(uid=account["id"], coinid=coinid,
		#												amount=amount + fee)
		#	data.update(add_active)
		#	self.set_status(add_active["error"])
		#	self.write(data)
		#	raise tornado.web.Finish

		# Submit amount from frozen balance
		sub_frozen = await self.account.balance.sub_frozen(uid=account["id"], 
													coinid=coinid, amount=amount + fee)
		if "error" in sub_frozen.keys():			
		
			data.update(sub_frozen)
			self.set_status(sub_frozen["error"])
			self.write(data)
			raise tornado.web.Finish
		logging.debug("\n               Sub frozen")
		logging.debug(sub_frozen)

		await self.account.save_transaction(txid=txid.get("txid"), coinid=coinid,
													amount=amount, address=address)

		# Return txid
		data.update(txid)
		self.write(data)

	def options(self):
		self.write(json.dumps(["GET", "POST"]))

















