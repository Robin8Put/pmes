# Builtins
import json
import logging
import sys

#Third-party
import tornado
from jsonrpcserver.aio import methods
import ujson

# Locals
from utils.tornado_components import web 
from utils.bip32keys.r8_ethereum.r8_eth import R8_Ethereum  
from utils.qtum_utils.qtum import Qtum
from utils import billing
from utils.models.account import Account
import settings

validator = {
		"QTUM": lambda x: Qtum.public_key_to_hex_address(x),
		"ETH": lambda x: R8_Ethereum.public_key_to_checksum_address(x)
}

class AllContentHandler(web.ManagementSystemHandler):
	"""Handles all blockchain content requests

	Endpoint: /api/blockchain/content

	Allowed methods: GET

	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	async def get(self):
		"""
		Accepts:
			without parameters

		Returns:
			list of dictionaries with following fields:
				- "description" - str
				- "read_access" - int
				- "write_access" - int
				- "cid" - int
				- "owneraddr" - str
				- "coinid" - str

		Verified: False
		"""
		contents = []

		for coinid in settings.AVAILABLE_COIN_ID:

			self.client_bridge.endpoint = settings.bridges[coinid]

			try:
				content = await self.client_bridge.request(method_name="getallcontent")
				if isinstance(content, dict):
					if "error" in content.keys():
						continue
				contents.extend(content)
			except:
				continue

		self.write(ujson.dumps(contents))
					

	def options(self):
		self.write(json.loads(["GET"]))


class ContentHandler(web.ManagementSystemHandler):
	"""Handles blockchain content requests

	Endpoint: /api/blockchain/[cid]/[coinid]/content

	Allowed method: GET, POST

	"""

	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')



	async def get(self, cid, coinid):
		"""Receives content by content id and coin id

		Accepts:
			Query string arguments:
				- "cid" - int
				- "coinid" - str

		Returns:
			return dict with following fields:
				- "description" - str
				- "read_access" - int
				- "write_access" - int
				- "content" - str
				- "cid" - int
				- "owneraddr" - str
				- "owner" - str
				- "coinid" - str

		Verified: True
		"""
		#super().verify()
		message = json.loads(self.get_argument("message", "{}"))

		public_key = message.get("public_key")

		# Set bridge url
		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		# Get content
		content = await self.client_bridge.request(method_name="getsinglecontent", cid=cid)

		if "error" in content.keys():
			self.set_status(content["error"])
			self.write(content)
			raise tornado.web.Finish 
		# Get owners account
		account = await self.client_storage.request(method_name="getaccountbywallet", 
														wallet=content["owneraddr"])
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		# Check if it is write or read access for content
		cids = await self.client_storage.request(method_name="getuserscontent",
															public_key=public_key)
		deals = await self.client_storage.request(method_name="getdeals", buyer=public_key)

		if int(content["cid"]) in [int(i[0]) for i in cids.get(coinid,[])]:
			content["access_type"] = "write_access"

		elif int(content["cid"]) in [int(i[0]) for i in deals.get(coinid,[])]:
			content["access_type"] = "read_access"

		try:
			offer = await self.client_bridge.request(method_name="get_offer", cid=cid, 
										buyer_address=validator[coinid](public_key))

			content["owner"] = account.get("public_key")
			content["seller_access_string"] = offer.get("seller_access_string")
			content["seller_pubkey"] = offer.get("seller_public_key")
		except:
			pass

		self.write(content)


	async def post(self, public_key, coinid):
		"""Writes content to blockchain

		Accepts:
			Query string args:
				- "public_key" - str
				- "coin id" - str
			Request body arguments:
				- message (signed dict as json):
					- "cus" (content) - str
					- "description" - str
					- "read_access" (price for read access) - int
					- "write_access" (price for write access) - int
				- signature

		Returns:
			- dictionary with following fields:
				- "owneraddr" - str
				- "description" - str
				- "read_price" - int
				- "write_price" - int

		Verified: True
		"""

		#super().verify()

		# Define genesis variables
		owneraddr = validator[coinid](public_key)    # Define owner address
		if coinid in settings.AVAILABLE_COIN_ID:     # Define bridge url
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coinid"})
			raise tornado.web.Finish 


		# Check if account exists
		account = await self.client_storage.request(method_name="getaccountdata", 
											public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish


		# Get message from request 
		try:
			data = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish

		if isinstance(data["message"], str):
			message = json.loads(data["message"])
		elif isinstance(data["message"], dict):
			message = data["message"]
		cus = message.get("cus")
		description = message.get("description")
		read_access = message.get("read_access")
		write_access = message.get("write_access")

		if sys.getsizeof(cus) > 1000000:
			self.set_status(403)
			self.write({"error":400, "reason":"Exceeded the content size limit."})
			raise tornado.web.Finish

		# Set fee
		fee = await billing.upload_content_fee(cus=cus, owneraddr=owneraddr, description=description)
		if "error" in fee.keys():
			self.set_status(fee["error"])
			self.write(fee)
			raise tornado.web.Finish

		# Send request to bridge
		data = {"cus":cus, 
				"owneraddr":owneraddr, 
				"description":description, 
				"read_price":read_access,
				"write_price":write_access
				}
		response = await self.client_bridge.request(method_name="makecid", **data)
		if "error" in response.keys():
			self.set_status(400)
			self.write(response)
			raise tornado.web.Finish

		# Write cid to database
		await self.client_storage.request(method_name="setuserscontent", public_key=public_key,
			hash=response["cus_hash"],coinid=coinid, txid=response["result"]["txid"],access="content")


		response = {i:data[i] for i in data if i != "cus"}
		self.write(response)


	def options(self, *args):
		self.write(json.dumps(["GET", "POST"]))




class DescriptionHandler(web.ManagementSystemHandler):
	"""Handles blockchain content description requests

	Endpoint: /api/blockchain/[cid]/description

	Allowed methods: PUT
	"""
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def put(self, cid):
		"""Update description for content

		Accepts:
			Query string args:
				- "cid" - int
			Request body parameters:
				- message (signed dict):
					- "description" - str
					- "coinid" - str

		Returns:
			dict with following fields:
				- "confirmed": None
				- "txid" - str
				- "description" - str
				- "content" - str
				- "read_access" - int
				- "write_access" - int
				- "cid" - int
				- "txid" - str
				- "seller_pubkey" - str
				- "seller_access_string": None or str
		
		Verified: True

		"""

		#super().verify()

		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish

		# Get data from signed message
		public_key = body.get("public_key", None)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		descr = message.get("description")
		coinid = message.get("coinid")

		# Check if all required data exists
		if not all([public_key, cid, descr]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish
		
		owneraddr = validator[coinid](public_key)

		# Get content owner
		response = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		if isinstance(response, dict):
			if "error" in response.keys():
				error_code = response["error"]
				self.set_status(error_code)
				self.write({"error":error_code, "reason":response["error"]})
				raise tornado.web.Finish

		# Check if current content belongs to current user
		if response != owneraddr:
			self.set_status(403)
			self.write({"error":403, "reason":"Owner does not match."})
			raise tornado.web.Finish

		# Set fee
		fee = await billing.update_description_fee(owneraddr=owneraddr,cid=cid, description=descr)

		# Set bridge url
		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coinid"})
			raise tornado.web.Finish 
		
		# Set description for content. Make request to the bridge
		request = await self.client_bridge.request(method_name="setdescrforcid", 
						cid=cid, descr=descr, owneraddr=owneraddr)
		if "error" in request.keys():
			self.set_status(request["error"])
			self.write(request)
			raise tornado.web.Finish

		self.write({"cid":cid, "description":descr, 
					"coinid":coinid, "owneraddr": owneraddr})


	def options(self, cid):
		self.write(json.dumps(["PUT"]))
	


class PriceHandler(web.ManagementSystemHandler):
	"""Handles content price requests
	"""


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'PUT, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def put(self, cid):
		"""Update price of current content

		Accepts:
			Query string args:
				- "cid" - int
			Request body params: 
				- "access_type" - str
				- "price" - int
				- "coinid" - str

		Returns:
			dict with following fields:
				- "confirmed": None
				- "txid" - str
				- "description" - str
				- "content" - str
				- "read_access" - int
				- "write_access" - int
				- "cid" - int
				- "txid" - str
				- "seller_pubkey" - str
				- "seller_access_string": None or str

		Verified: True

		""" 
		super().verify()

		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish

		# Get data from signed message	
		public_key = body.get("public_key", None)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		price = message.get("price")
		access_type = message.get("access_type")
		coinid = message.get("coinid")

		# Check if required fields exists
		if not any([price, access_type, coinid]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed price and access type for content"})

		# Set bridges url
		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coin ID"})
			raise tornado.web.Finish

		# Get public key hex or checksum format
		check = validator[coinid](public_key)

		# Get content owner address
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		if isinstance(owneraddr, dict):
			if "error" in owneraddr.keys():
				self.set_status(404)
				self.write({"error":404, "reason":"Owner not found."})
				raise tornado.web.Finish

		# Check if current content belongs to current user
		if owneraddr != check:
			self.set_status(403)
			self.write({"error":403, "reason":"Owner does not match."})
			raise tornado.web.Finish

		response = {"cid":cid, "coinid":coinid}

		# Make setprice request to the bridge
		if access_type == "write_price":
			result = await self.client_bridge.request(method_name="set_write_price", 
														cid=cid, write_price=price)
			response["write_access"] = result["price"]

		elif access_type == "read_price":
			result = await self.client_bridge.request(method_name="set_read_price", 
												cid=cid, read_price=price)
			response["read_access"] = result["price"]


		# Fee
		fee = await billing.set_price_fee(cid=cid, price=price, owneraddr=owneraddr)
		if "error" in fee.keys():
			self.set_status(fee["error"])
			self.write(fee)
			raise tornado.web.Finish

		self.write(response)


	def options(self, cid):
		self.write(json.dumps(["GET", "PUT"]))



class WriteAccessOfferHandler(web.ManagementSystemHandler):
	"""Handles requests binded with offers (make, reject etc)

	Endpoint: /api/blockchain/[public_key]/write-access-offer

	Allowed methods: POST, PUT

	"""

	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, PUT, OPTIONS')


	async def post(self, public_key=None):
		"""Creates a new offer with freezing balance

		Accepts:
			Query string args:
				- buyer public key
			Request body params:
				- "cid" - int
				- "buyer access string" - str
				- "coinid" - str
				- "write_price" - int

		Returns:
			dict with following fields:
				- "owner_pubkey" - str
				- "buyer_address" - str
				- "cid" - cid
				- "access_type" - str
				- "txid" - str
				- "owner_addr" - str
				- "price" - int
				- "confirmed": None

		Verified: True

		"""

		super().verify()
		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish

		# Get data from signed message
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		write_price = message.get("price")
		coinid = message.get("coinid")
		buyer_access_string = message.get("buyer_access_string")

		# Check if required fields exists
		if not all([buyer_access_string, coinid, str(cid).isdigit()]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish

		# Set bridge url
		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coinid"})
			raise tornado.web.Finish 

		# Get cid price from bridge if the does not specified
		if not write_price:
			write_price = await self.client_bridge.request(method_name="get_write_price", cid=cid)

		# Get public key hex or checksum format
		buyer_address = validator[coinid](public_key)

		# Get owner address
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)

		# Check if public key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
													public_key=public_key)
		if "error" in account.keys():
			# If account does not exist
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		#Get buyers balance
		balances = await self.client_balance.request(method_name="getbalance", 
													coinid=coinid, uid=account["id"])

		# Check if current content belongs to current user
		if owneraddr == buyer_address:
			self.set_status(400)
			self.write({"error":400, 
						"reason":"Content belongs to current user"})
			raise tornado.web.Finish

		# Get difference with balance and price
		for w in balances:
			if "PUT" in w.values():
				balance = w 
		difference = int(balance["amount"]) - int(write_price)

		if difference < 0:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Balance is not enough"})
			raise tornado.web.Finish

		# Send request to bridge
		offer_data = {
			"cid":cid,
			"write_price":write_price,
			"offer_type":1,
			"buyer_address": buyer_address,
			"buyer_access_string":buyer_access_string
		}
		response = await self.client_bridge.request(method_name="make_offer", **offer_data)
		try:
			response["error"]
		except:
			pass
		else:
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		await self.client_storage.request(method_name="insertoffer", cid=cid, 
											txid=response["result"]["txid"], 
											coinid=coinid, public_key=public_key)

		# Send e-mail to seller
		seller = await self.client_storage.request(method_name="getaccountbywallet",wallet=owneraddr)
		if "error" in seller.keys():
			self.set_status(seller["error"])
			self.write(seller)
			raise tornado.web.Finish

		if seller.get("email"):
			emaildata = {
				"to": seller["email"],
				"subject": "Robin8 support",
     			"optional": "You`ve got an offer for content %s." % cid
			}
			await self.client_email.request(method_name="sendmail", **emaildata)


		# Freeze price at balance
		await self.client_balance.request(method_name="depositbalance", uid=account["id"],
															coinid=coinid, amount=write_price)
		response["offer_type"] = "write_access"
		del response["result"]		
		self.write(response)


	async def put(self, public_key=None):
		"""Reject offer and unfreeze balance
		
		Accepts:
			- cid
			- buyer public key
			- buyer address
		"""
		super().verify()
		# Check if message contains required data
		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
			
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = int(message["offer_id"].get("cid", 0))
		buyer_address = message["offer_id"].get("buyer_address")
		coinid = message.get("coinid")

		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coin ID"})
			raise tornado.web.Finish

		check = validator[coinid](public_key)

		account = await self.client_storage.request(method_name="getaccountdata", 
															public_key=public_key)
		if "error" in account.keys():
			error_code = account["error"]
			self.set_status(error_code)
			self.write(account)
			raise tornado.web.Finish
	
		# Check if one of sellers or buyers rejects offer
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		hex_ = check
		if buyer_address != hex_ and owneraddr != hex_:
			# Avoid rejecting offer
			self.set_status(403)
			self.write({"error": 403, "reason":"Forbidden. Offer does not belong to user."})
		
		# Reject offer
		response = await self.client_bridge.request(method_name="reject_offer",
										coinid=coinid, cid=cid, buyer_address=buyer_address)
		if "error" in response.keys():
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		# Get buyer for email sending
		buyer = await self.client_storage.request(method_name="getaccountbywallet",
																wallet=buyer_address)
		if "error" in buyer.keys():
			self.set_status(buyer["error"])
			self.write(buyer)
			raise tornado.web.Finish
	
		if buyer.get("email"):
			emaildata = {
				"to": buyer.get("email"),
				"subject": "Robin8 support",
     			"optional": "Your offer with cid %s was rejected." % cid
			}
			await self.client_email.request(method_name="sendmail", **emaildata)
		
		# Undeposit balance
		price = await self.client_bridge.request(method_name="get_write_price", cid=cid)
		await self.client_balance.request(method_name="undepositbalance", uid=buyer["id"],
														coinid=coinid, amount=price)

		del response["result"]
		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["PUT", "POST"]))


class ReadAccessOfferHandler(web.ManagementSystemHandler):
	"""Handles requests binded with offers (make, reject etc)
	"""
	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, PUT, OPTIONS')


	async def post(self, public_key=None):
		"""Creates new offer

		Accepts:
			- buyer public key
			- cid
			- buyer access string
		Returns:
			- offer parameters as dictionary
		"""
		super().verify()
		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		read_price = message.get("price")
		coinid = message.get("coinid")
		buyer_access_string = message.get("buyer_access_string")
	
		if not all([buyer_access_string, coinid, str(cid).isdigit()]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish

		# Set bridge url
		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coinid"})
			raise tornado.web.Finish 

		# Get cid price from bridge
		if not read_price:
			read_price = await self.client_bridge.request(method_name="get_read_price", cid=cid)

		buyer_address = validator[coinid](public_key)
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", 
													cid=cid)

		# Check if public key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
									public_key=public_key)
		if "error" in account.keys():
			# If account does not exist
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		#Get sellers balance
		balances = await self.client_balance.request(method_name="getbalance", 
											coinid=coinid, uid=account["id"])

		# Check if current content does not belong to current user
		if owneraddr == buyer_address:
			self.set_status(400)
			self.write({"error":400, 
						"reason":"Content belongs to current user"})
			raise tornado.web.Finish

		# Get difference with balance and price
		for w in balances:
			if "PUT" in w.values():
				balance = w 
		difference = int(balance["amount"]) - int(read_price)
		if difference < 0:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Balance is not enough"})
			raise tornado.web.Finish

		# Send request to bridge
		offer_data = {
			"cid":cid,
			"read_price":read_price,
			"offer_type":0,
			"buyer_address": buyer_address,
			"buyer_access_string":buyer_access_string
		}
		response = await self.client_bridge.request(method_name="make_offer", 
													**offer_data)
		try:
			response["error"]
		except:
			pass
		else:
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		await self.client_storage.request(method_name="insertoffer", cid=cid, 
											txid=response["result"]["txid"], 
											coinid=coinid, public_key=public_key)
		# Send e-mail to seller
		seller = await self.client_storage.request(method_name="getaccountbywallet",wallet=owneraddr)
		if "error" in seller.keys():
			self.set_status(seller["error"])
			self.write(seller)
			raise tornado.web.Finish

		if seller.get("email"):
			emaildata = {
				"to": seller["email"],
				"subject": "Robin8 support",
     			"optional": "You`ve got an offer for content %s." % cid
			}
			await self.client_email.request(method_name="sendmail", **emaildata)


		# Freeze price at balance
		await self.client_balance.request(method_name="depositbalance", uid=account["id"],
															coinid=coinid, amount=read_price)
		response["offer_type"] = "read_access"
		del response["result"]		

		self.write(response)


	async def put(self, public_key):
		"""Reject offer

		Accepts:
			- cid
			- buyer public key
			- buyer address
		"""
		super().verify()
		# Check if message contains required data
		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
			
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = int(message["offer_id"].get("cid", 0))
		buyer_address = message["offer_id"].get("buyer_address")
		coinid = message.get("coinid")

		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coin ID"})
			raise tornado.web.Finish

		check = validator[coinid](public_key)

		account = await self.client_storage.request(method_name="getaccountdata", 
															public_key=public_key)
		if "error" in account.keys():
			error_code = account["error"]
			self.set_status(error_code)
			self.write(account)
			raise tornado.web.Finish

	
		# Check if one of sellers or buyers rejects offer
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		hex_ = check
		if buyer_address != hex_ and owneraddr != hex_:
			# Avoid rejecting offer
			self.set_status(403)
			self.write({"error": 403, "reason":"Forbidden. Offer does not belong to user."})
		
		# Reject offer
		response = await self.client_bridge.request(method_name="reject_offer",
										coinid=coinid, cid=cid, buyer_address=buyer_address)
		if "error" in response.keys():
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		# Get buyer for email sending
		buyer = await self.client_storage.request(method_name="getaccountbywallet",
																wallet=buyer_address)
		if "error" in buyer.keys():
			self.set_status(buyer["error"])
			self.write(buyer)
			raise tornado.web.Finish
	
		if buyer.get("email"):
			emaildata = {
				"to": buyer.get("email"),
				"subject": "Robin8 support",
     			"optional": "Your offer with cid %s was rejected." % cid
			}
			await self.client_email.request(method_name="sendmail", **emaildata)
		

		price = await self.client_bridge.request(method_name="get_write_price", cid=cid)
		await self.client_balance.request(method_name="undepositbalance", uid=buyer["id"],
														coinid=coinid, amount=price)

		del response["result"]
		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["PUT", "POST"]))



class DealHandler(web.ManagementSystemHandler):
	"""Handles accept offer requests
	"""

	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

	async def post(self, public_key):
		"""Accepting offer by buyer

		Function accepts:
			- cid
			- buyer access string
			- buyer public key
			- seller public key
		"""
		super().verify()
		# Check if message contains required data
		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
			
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]

		cid = message.get("cid")
		buyer_pubkey = message.get("buyer_pubkey")
		buyer_access_string = message.get("buyer_access_string")

		seller_access_string = message.get("seller_access_string")
		access_type = message.get("access_type")

		coinid = message.get("coinid")
		# check passes data
		if not all([buyer_access_string, cid, buyer_pubkey]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish

		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coin ID"})
			raise tornado.web.Finish 

		# Sellcontent
		buyer_address = validator[coinid](buyer_pubkey)

		# Check if accounts exists
		seller_account = await self.client_storage.request(method_name="getaccountdata", 
																	public_key=public_key)

		try:
			error_code = seller_account["error"]
		except:
			pass
		else:
			self.set_status(error_code)
			self.write(seller_account)
			raise tornado.web.Finish

		buyer_account = await self.client_storage.request(method_name="getaccountdata", 
										public_key=buyer_pubkey)
		try:
			error_code = buyer_account["error"]
		except:
			pass
		else:
			self.set_status(error_code)
			self.write(buyer_account)
			raise tornado.web.Finish

		# Check if content belongs to current account
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		
		if owneraddr != validator[coinid](public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Forbidden. Profile owner does not match."})
			raise tornado.web.Finish

		#Get buyers balance
		balances = await self.client_balance.request(method_name="getbalance", 
								coinid=coinid, uid=buyer_account["id"])
		if isinstance(balances, dict):
			if "error" in balances.keys():
				self.set_status(balances["error"])
				self.write(balances)
				raise tornado.web.Finish 


		# Get difference with balance and price
		get_price = await self.client_bridge.request(method_name="get_offer", cid=cid, 
														buyer_address=buyer_address)
		price = get_price["price"]

		for w in balances:
			if "PUT" in w.values():
				balance = w

		difference = int(balance["deposit"]) - int(price)

		if difference >= 0:

			if access_type == "write_access":
				# Fee
				fee = await billing.change_owner_fee(cid=cid, new_owner=buyer_pubkey)
				if "error" in fee.keys():
					self.set_status(fee["error"])
					self.write(fee)
					raise tornado.web.Finish
			
				# Change content owner
				chownerdata = {
					"cid":cid,
					"new_owner": buyer_address,
					"access_string": buyer_access_string,
					"seller_public_key": public_key
				}

				response = await self.client_bridge.request(method_name="changeowner", 
														**chownerdata)

				await self.client_storage.request(method_name="changeowner", cid=cid, 
									public_key=buyer_account["public_key"], coinid=coinid)

			elif access_type == "read_access":

				# Fee
				fee = await billing.sell_content_fee(cid=cid, new_owner=buyer_pubkey)

				if "error" in fee.keys():
					self.set_status(fee["error"])
					self.write(fee)
					raise tornado.web.Finish

				selldata = {
					"cid":cid,
					"buyer_address":buyer_address,
					"access_string":buyer_access_string,
					"seller_public_key":public_key
				}

				response = await self.client_bridge.request(method_name="sellcontent", 
														**selldata)

				# Write cid to database
				await self.client_storage.request(method_name="setuserscontent", 
											public_key=buyer_account["public_key"], 
											hash=None,coinid=coinid, cid=cid,
											txid=response["result"]["txid"],
											access="deal")

			
			# Increment and decrement balances of seller and buyer
			await self.client_balance.request(method_name="undepositbalance", 
													uid=buyer_account["id"],
													amount=price, coinid=coinid)

			await self.client_balance.request(method_name="decbalance", 
												uid=buyer_account["id"], amount=price)

			await self.client_balance.request(method_name="incbalance", 
												txid=response["result"]["txid"], 
												uid=seller_account["id"], amount=price, 
												coinid=coinid)

			del response["result"]
			del response["contract_owner_hex"]
			self.write(response)
		else:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Insufficient funds of buyer"})
			raise tornado.web.Finish


	def options(self, public_key):
		self.write(json.dumps(["POST"]))


class ReviewsHandler(web.ManagementSystemHandler):
	""" Reviews handler class """

	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


	async def get(self, cid, coinid):
		"""Receives all contents reviews
		"""

		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]


		reviews = await self.client_bridge.request(method_name="get_reviews", cid=cid)
		if isinstance(reviews, dict):
			if "error" in reviews:
				self.set_status(500)
				self.write(reviews)
				raise tornado.web.Finish

		for review in reviews:
			review["confirmed"] = 1

		storage_reviews = await self.client_storage.request(method_name="getreviews", 
															coinid=coinid, cid=cid)

		if isinstance(reviews, dict):
			if "error" in reviews.keys():
				self.set_status(reviews["error"])
				self.write(reviews)
				raise tornado.web.Finish
		
		self.write(json.dumps(reviews + storage_reviews))


	async def options(self, cid, coinid):
		self.write(json.dumps(["GET"]))


class ReviewHandler(web.ManagementSystemHandler):
	"""Handles all blockchain content requests
	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	async def post(self, public_key):
		"""Writes contents review
		"""
		try:
			body = json.loads(self.request.body)
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Unexpected data format. JSON required"})
			raise tornado.web.Finish
			
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]

		cid = message.get("cid")
		review = message.get("review")
		rating = message.get("rating")
		coinid = message.get("coinid")

		if not all([cid, rating, review]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})

		if coinid in settings.AVAILABLE_COIN_ID:
			self.client_bridge.endpoint = settings.bridges[coinid]
		else:
			self.set_status(400)
			self.write({"error":400, "reason":"Invalid coinid"})
			raise tornado.web.Finish 

		buyer_address = validator[coinid](public_key)

		review = await self.client_bridge.request(method_name="add_review", cid=int(cid),
																buyer_address=buyer_address,
																stars=int(rating), review=review)
		await self.client_storage.request(method_name="setreview", cid=cid, 
										txid=review["result"]["txid"], coinid=coinid)

		self.write({"cid":cid, "review":review, "rating":rating})

	def options(self, public_key):
		self.write(json.dumps(["GET, POST"]))


class DealsHandler(web.ManagementSystemHandler):

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	async def get(self, public_key):
		cids = await self.client_storage.request(method_name="getdeals", buyer=public_key)
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
				if isinstance(contents, dict):
					if "error" in contents.keys():
						continue
				container.extend(contents)
			except:
				continue

		self.write(json.dumps(container))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))