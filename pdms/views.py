# Builtins
import json
import logging

#Third-party
import tornado
from tornado import gen
import tornado_components.web 
from jsonrpcserver.aio import methods
from jsonrpcclient.http_client import HTTPClient
from qtum_utils.qtum import Qtum
import settings
from utils import billing



class AllContentHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles all blockchain content requests
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
		"""Returns all content as list 
		"""
		# List for contents
		content = await self.client_storage.request(method_name="getallcontent")
		try:
			content["error"]
		except:
			self.write(json.dumps(content))
		else:
			self.set_status(content["error"])
			self.write(content)

	def options(self):
		self.write(json.loads(["GET"]))


class ContentHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles blockchain content requests
	"""

	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


	async def get(self, cid):
		"""Receives content by content id
		"""
		logging.debug("[+] -- Get single content")
		content = await self.client_storage.request(method_name="getsinglecontent", 
																		cid=cid)
		logging.debug(content)
		if "error" in content.keys():
			self.set_status(content["error"])
			self.write(content)
			raise tornado.web.Finish 

		self.write(content)


	async def post(self, public_key=None):
		"""Writes content to blockchain

		Accepts:
			- cus (content)
			- public_key

		"""
		logging.debug("[+] -- Post content to blockchain")
		#super().verify()
		# Check if public_key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
											public_key=public_key)

		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		# Get message from request 
		data = json.loads(self.request.body)
		if not data:
			self.set_status(403)
			self.write({"error":403, "reason":"Forbidden"})
			raise tornado.web.Finish
		logging.debug(data)
		# Overload data dictionary
		if isinstance(data["message"], str):
			message = json.loads(data["message"])
		elif isinstance(data["message"], dict):
			message = data["message"]
		cus = message.get("cus", None)
		description = message.get("description", None)
		read_access = message.get("read_access", 0)
		write_access = message.get("write_access", 0)
	
		# Send requests to bridge
		owneraddr = Qtum.public_key_to_hex_address(public_key)
		data = {"cus":cus, 
				"owneraddr":owneraddr, 
				"description":description, 
				"read_price":read_access,
				"write_price":write_access
				}
		logging.debug(data)
		response = await self.client_bridge.request(method_name="makecid", **data)
		if "error" in response.keys():
			self.set_status(400)
			self.write(response)
			raise tornado.web.Finish
		# Set fee
		fee = await billing.upload_content_fee(cus=cus, owneraddr=owneraddr,
															description=description)

		# Write content to database
		contentdata = {"txid":response["result"]["txid"], "account_id":account["id"],
						"read_access":read_access, "write_access":write_access, 
						"description":description, "content":cus,
						"seller_pubkey":None, "seller_access_string":None}
		result = await self.client_storage.request(method_name="setuserscontent", 
																**contentdata)
		if "error" in result.keys():
			self.set_status(result["error"])
			self.write(result)

		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["GET", "POST"]))



class DescriptionHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles blockchain content description requests
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
		"""Set description for content
		"""
		#super().verify()
		body = json.loads(self.request.body)
		public_key = body.get("public_key", None)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		descr = message.get("description")
		if not all([public_key, cid, descr]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish
		
		# Get content owner
		response = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		if isinstance(response, dict):
			if "error" in response.keys():
				error_code = response["code"]
				self.set_status(error_code)
				self.write({"error":error_code, "reason":response["error"]})
				raise tornado.web.Finish

		# Check if content owner has current public key 
		if not response == Qtum.public_key_to_hex_address(public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Owner does not match."})
			raise tornado.web.Finish

		# Set fee
		#fee = billing.update_description_fee(owneraddr=Qtum.public_key_to_hex_address(public_key),
		#													cid=cid, description=descr)
		# Set description for content
		request = await self.client_bridge.request(method_name="setdescrforcid", 
						cid=cid, descr=descr, owneraddr=response)
		if "error" in request.keys():
			self.set_status(request["error"])
			self.write(request)
			raise tornado.web.Finish
		self.write(request)


	def options(self, cid):
		self.write(json.dumps(["PUT"]))
	


class PriceHandler(tornado_components.web.ManagementSystemHandler):
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
		"""Sets price for blockchain content

		Accepts:
			- cid
			- owners public key
			- price
		""" 
		#super().verify()
		body = json.loads(self.request.body)
		public_key = body.get("public_key", None)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		read_price = message.get("read_price", "")
		write_price = message.get("write_price", "")
		descr = message.get("description")
		
		if not any([read_price, write_price]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed price for content"})
		# Check if current public key is content owner
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		if isinstance(owneraddr, dict):
			if "error" in owneraddr.keys():
				self.set_status(404)
				self.write({"error":404, "reason":"Owner not found."})
				raise tornado.web.Finish

		if not owneraddr == Qtum.public_key_to_hex_address(public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Owner does not match."})
			raise tornado.web.Finish
		# Make setprice request to the bridge
		if write_price:
			updated = await self.client_bridge.request(method_name="set_write_price", 
																cid=cid, write_price=write_price)
		elif read_price:
			updated = await self.client_bridge.request(method_name="set_read_price", 
																cid=cid, write_price=write_price)

		self.write(updated)

	def options(self, cid):
		self.write(json.dumps(["GET", "PUT"]))



class WriteAccessOfferHandler(tornado_components.web.ManagementSystemHandler):
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
		#super().verify()
		body = json.loads(self.request.body)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		write_price = message.get("write_price")
		buyer_access_string = message.get("buyer_access_string")
		# Get cid price from bridge
		if not write_price:
			content = await self.client_storage.request(method_name="getsinglecontent", cid=cid)
			write_price = content["write_access"]
			
		if not all([message, buyer_access_string, str(cid).isdigit()]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish

		# Check if public key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
									public_key=public_key)
		if "error" in account.keys():
			# If account does not exist
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		# Check if current offer already exists
		offer = await self.client_storage.request(method_name="getoffer",
			cid=cid, buyer_address=Qtum.public_key_to_hex_address(public_key))
		if "cid" in offer.keys():
			self.set_status(403)
			self.write({"error":403,
						"reason":"Current offer already exists"})
			raise tornado.web.Finish


		#Get sellers balance
		balance = await self.client_balance.request(method_name="getbalance", 
													uid=account["id"])
		#Detect contents owner
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", 
													cid=cid)
	
		if owneraddr == Qtum.public_key_to_hex_address(public_key):
			self.set_status(400)
			self.write({"error":400, 
						"reason":"Content belongs to current user"})
			raise tornado.web.Finish

		# Get difference with balance and price
		difference = int(balance["amount"]) - int(write_price)
		if difference < 0:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Balance is not enough"})
			raise tornado.web.Finish

		# Make offer
		buyer_address = Qtum.public_key_to_hex_address(public_key)
		offer_data = {
			"cid":cid,
			"write_price":write_price,
			"offer_type":1,
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

		# Send e-mail to seller
		seller = await self.client_storage.request(method_name="getaccountbywallet",
											wallet=owneraddr)
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

		# Insert offer to database
		await self.client_storage.request(method_name="insertoffer", 
				owner_pubkey=seller["public_key"], owner_addr=owneraddr,
				txid=response["result"]["txid"], access_type="write_access",
				cid=cid, price=write_price, buyer_address=buyer_address)

		await self.client_balance.request(method_name="depositbalance", uid=account["id"],
																		amount=write_price)

		self.write(response)


	async def put(self, public_key=None):
		"""Reject offer

		Accepts:
			- cid
			- buyer public key
			- buyer address
		"""
		#super().verify()
		# Check if message contains required data
		body = json.loads(self.request.body)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message["offer_id"].get("cid", 0)
		cid = int(cid)
		buyer_address = message["offer_id"].get("buyer_address")

		account = await self.client_storage.request(method_name="getaccountdata", 
										public_key=public_key)
		if "error" in account.keys():
			error_code = account["error"]
			self.set_status(error_code)
			self.write(account)
			raise tornado.web.Finish

		# Check if current offer exists
		offer = await self.client_storage.request(method_name="getoffer",
									cid=cid, buyer_address=buyer_address)
		if not "cid" in offer.keys():
			self.set_status(400)
			self.write({"error":400,
						"reason":"Current offer does not exist"})
			raise tornado.web.Finish
	
		# Check if one of sellers or buyers rejects offer
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		
		hex_ = Qtum.public_key_to_hex_address(public_key)
		if buyer_address != hex_ and owneraddr != hex_:
			# Avoid rejecting offer
			self.set_status(403)
			self.write({"error": 403, "reason":"Forbidden"})
		# Reject offer
		response = await self.client_bridge.request(method_name="reject_offer",
										cid=cid, buyer_address=buyer_address)
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
		# Unfreeze balance
		get_offer = await self.client_storage.request(method_name="getoffer", cid=cid,
														buyer_address=buyer_address)
		await self.client_balance.request(method_name="undepositbalance", uid=buyer["id"],
																amount=get_offer["price"])
		# Remove offer from database
		rejected = await self.client_storage.request(method_name="removeoffer",
						cid=cid, buyer_address=buyer_address)
		if "error" in rejected.keys():
			self.set_status(rejected["error"])
			self.write(rejected)
			raise tornado.web.Finish

		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["PUT", "POST"]))


class ReadAccessOfferHandler(tornado_components.web.ManagementSystemHandler):
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
		#super().verify()
		body = json.loads(self.request.body)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		read_price = message.get("read_price")
		buyer_access_string = message.get("buyer_access_string")
		# Get cid price from bridge
		if not read_price:
			content = await self.client_storage.request(method_name="getsinglecontent", cid=cid)
			read_price = content["read_access"]
			
		if not all([message, buyer_access_string, str(cid).isdigit()]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish

		# Check if public key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
									public_key=public_key)
		if "error" in account.keys():
			# If account does not exist
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		# Check if current offer already exists
		offer = await self.client_storage.request(method_name="getoffer",
			cid=cid, buyer_address=Qtum.public_key_to_hex_address(public_key))
		if "cid" in offer.keys():
			self.set_status(403)
			self.write({"error":403,
						"reason":"Current offer already exists"})
			raise tornado.web.Finish


		#Get sellers balance
		balance = await self.client_balance.request(method_name="getbalance", 
													uid=account["id"])
		#Detect contents owner
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", 
													cid=cid)
	
		if owneraddr == Qtum.public_key_to_hex_address(public_key):
			self.set_status(400)
			self.write({"error":400, 
						"reason":"Content belongs to current user"})
			raise tornado.web.Finish

		# Get difference with balance and price
		difference = int(balance["amount"]) - int(read_price)
		if difference < 0:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Balance is not enough"})
			raise tornado.web.Finish

		# Make offer
		buyer_address = Qtum.public_key_to_hex_address(public_key)
		offer_data = {
			"cid":cid,
			"offer_type":0,
			"read_price":read_price,
			"buyer_address": buyer_address,
			"buyer_access_string":buyer_access_string
		}
		response = await self.client_bridge.request(method_name="make_offer", 
													**offer_data)
		logging.debug("[+] -- Read access debugging")
		logging.debug(response)
		try:
			response["error"]
		except:
			pass
		else:
			self.set_status(response["error"])
			self.write(response)
			raise tornado.web.Finish

		# Send e-mail to seller
		seller = await self.client_storage.request(method_name="getaccountbywallet",
											wallet=owneraddr)
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

		# Insert offer to database
		await self.client_storage.request(method_name="insertoffer", 
				owner_pubkey=seller["public_key"], owner_addr=owneraddr,
				txid=response["result"]["txid"], access_type="read_access",
				cid=cid, price=read_price, buyer_address=buyer_address)
		await self.client_balance.request(method_name="depositbalance", uid=account["id"],
																		amount=read_price)

		self.write(response)


	async def put(self, public_key=None):
		"""Reject offer

		Accepts:
			- cid
			- buyer public key
			- buyer address
		"""
		#super().verify()
		# Check if message contains required data
		body = json.loads(self.request.body)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message["offer_id"].get("cid", 0)
		cid = int(cid)
		buyer_address = message["offer_id"].get("buyer_address")

		account = await self.client_storage.request(method_name="getaccountdata", 
										public_key=public_key)
		if "error" in account.keys():
			error_code = account["error"]
			self.set_status(error_code)
			self.write(account)
			raise tornado.web.Finish

		# Check if current offer exists
		offer = await self.client_storage.request(method_name="getoffer",
									cid=cid, buyer_address=buyer_address)
		if not "cid" in offer.keys():
			self.set_status(400)
			self.write({"error":400,
						"reason":"Current offer does not exist"})
			raise tornado.web.Finish
	
		# Check if one of sellers or buyers rejects offer
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
	
		hex_ = Qtum.public_key_to_hex_address(public_key)
		if buyer_address != hex_ and owneraddr != hex_:
			# Avoid rejecting offer
			self.set_status(403)
			self.write({"error": 403, "reason":"Forbidden"})
		# Reject offer
		response = await self.client_bridge.request(method_name="reject_offer",
										cid=cid, buyer_address=buyer_address)
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
		# Unfreeze balance
		get_offer = await self.client_storage.request(method_name="getoffer", cid=cid,
														buyer_address=buyer_address)
		logging.debug("[+] -- Reject read access")
		logging.debug(get_offer)
		await self.client_balance.request(method_name="undepositbalance", uid=buyer["id"],
																amount=get_offer["price"])
		# Remove offer from database
		rejected = await self.client_storage.request(method_name="removeoffer",
						cid=cid, buyer_address=buyer_address)
		if "error" in rejected.keys():
			self.set_status(rejected["error"])
			self.write(rejected)
			raise tornado.web.Finish

		self.write(response)


	def options(self, public_key):
		self.write(json.dumps(["PUT", "POST"]))



class DealHandler(tornado_components.web.ManagementSystemHandler):
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

	async def post(self, public_key=None):
		"""Accepting offer by buyer

		Function accepts:
			- cid
			- buyer access string
			- buyer public key
			- seller public key
		"""
		#super().verify()
		# Check if message contains required data
		logging.debug("[+] -- DealHandler")
		body = json.loads(self.request.body)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		cid = message.get("cid")
		buyer_pubkey = message.get("buyer_pubkey")
		buyer_access_string = message.get("buyer_access_string")
		seller_access_string = message.get("seller_access_string")
		access_type = message.get("access_type")
		logging.debug(body)
		# check passes data
		if not all([buyer_access_string, cid, buyer_pubkey]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish

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

		if owneraddr != Qtum.public_key_to_hex_address(public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Forbidden."})
			raise tornado.web.Finish

		# Check if current offer exists
		offer = await self.client_storage.request(method_name="getoffer",
			cid=cid, buyer_address=Qtum.public_key_to_hex_address(buyer_pubkey))
		if "error" in offer.keys():
			self.set_status(offer["error"])
			self.write(offer)
			raise tornado.web.Finish

		#buyer_access_string = Qtum.to_compressed_public_key(buyer_access_string)

		#Get buyers balance
		balance = await self.client_balance.request(method_name="getbalance", 
										uid=buyer_account["id"])
		if "error" in balance.keys():
			self.set_status(balance["error"])
			self.write(balance)
			raise tornado.web.Finish 

		# Get difference with balance and price
		price = int(offer["price"])
		difference = int(balance["deposit"]) - price
		if difference >= 0:

			# Write access string to database
			setaccessdata = {
				"cid":cid,
				"seller_access_string": seller_access_string,
				"seller_pubkey": public_key
			}
			res = await self.client_storage.request(method_name="setaccessstring",
															**setaccessdata)

			# Sellcontent
			selldata = {
				"cid":cid,
				"buyer_address":Qtum.public_key_to_hex_address(buyer_pubkey),
				"access_string":buyer_access_string
			}
			logging.debug("[+] -- Sell data")
			logging.debug(selldata)
			sell = await self.client_bridge.request(method_name="sellcontent", 
													**selldata)
			
			# Check if selling was successfull
			try:
				sell["content_owner"]
			except:
				self.set_status(500)
				self.write({"error":500, "reason":"Unpossible to implement selling."})
				raise tornado.web.Finish
			else:

				# Increment and decrement balances of seller and buyer
				await self.client_balance.request(method_name="undepositbalance", 
														uid=buyer_account["id"],
														amount=price)
				await self.client_balance.request(method_name="decbalance", 
									uid=buyer_account["id"], amount=price)
				await self.client_balance.request(method_name="incbalance", 
									uid=seller_account["id"], amount=price)

				# Remove offer from database
				await self.client_storage.request(method_name="removeoffer",cid=cid,
						buyer_address=Qtum.public_key_to_hex_address(buyer_pubkey))

				# Change owner in database
				if access_type == "write_access":
					await self.client_storage.request(method_name="changecontentowner",
													cid=cid, buyer_pubkey=buyer_pubkey)
					# Change content owner
					chownerdata = {
						"cid":cid,
						"new_owner": Qtum.public_key_to_hex_address(buyer_pubkey),
						"access_string": buyer_access_string
					}
					await self.client_bridge.request(method_name="changeowner", 
															**chownerdata)
				else:
					await self.client_storage.request(method_name="addcontentowner", cid=cid, 
														buyer_pubkey=buyer_pubkey)
				
				# Write deal to database
				deal_data = {
					"cid":cid,
					"access_type":access_type,
					"buyer":buyer_pubkey,
					"publisher":public_key,
					"price":price
				}
				await self.client_storage.request(method_name="writedeal", **deal_data)
				
				self.write({"result":"ok"})
		else:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Insufficient funds"})


	def options(self, public_key):
		self.write(json.dumps(["POST"]))


class ReviewsHandler(tornado_components.web.ManagementSystemHandler):
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


	async def get(self, cid):
		"""Receives all contents reviews
		"""
		reviews = await self.client_storage.request(method_name="getreviews", cid=cid)
		if isinstance(reviews, dict):
			if "error" in reviews.keys():
				self.set_status(reviews["error"])
				self.write(reviews)
				raise tornado.web.Finish
		self.write(json.dumps(reviews))


	async def options(self, cid):
		self.write(json.dumps(["GET"]))


class ReviewHandler(tornado_components.web.ManagementSystemHandler):
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
		logging.debug("[+] -- ReviewHandler")
		body = json.loads(self.request.body)
		if isinstance(body["message"], str):
			message = json.loads(body["message"])
		elif isinstance(body["message"], dict):
			message = body["message"]
		logging.debug("\n" + json.dumps(body) + "\n")

		cid = message.get("cid")
		review = message.get("review")
		rating = message.get("rating")

		if not all([cid, rating, review]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})

		bridge_review = await self.client_bridge.request(method_name="add_review", cid=cid,
										buyer_address=Qtum.public_key_to_hex_address(public_key),
										stars=rating, review=review)
		logging.debug(bridge_review)

		review = await self.client_storage.request(method_name="setreview", cid=cid,
											rating=rating, review=review, public_key=public_key)
		logging.debug(review)

		if "error" in review.keys():
			self.set_status(review["error"])
			self.write(review)
			raise tornado.web.Finish

		self.write(review)

	def options(self, public_key):
		self.write(json.dumps(["GET, POST"]))


class DealsHandler(tornado_components.web.ManagementSystemHandler):

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
		deal1 = {"cid":1, "offer_type":"write_access", 
				"user": "public_key", "owner":"public_key", "price": 10}
		deal2 = {"cid":2, "offer_type":"write_access", 
				"user": "public_key", "owner":"public_key", "price": 10}
		self.write(json.dumps([deal1, deal2]))

	def options(self, public_key):
		self.write(json.dumps(["GET"]))