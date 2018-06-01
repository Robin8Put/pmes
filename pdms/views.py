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



class AllContentHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles all blockchain content requests
	"""

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email

	async def get(self):
		"""Returns all content as list 
		"""
		# List for contents
		container = []
		counter = 1
		while True:
			# Get description
			descr = await self.client_bridge.request(method_name="ownerbycid", 
													cid=counter)
			if not all(descr.values()):
				break
			else:
				# Get Owner address
				owneraddr = await self.client_bridge.request(method_name="ownerbycid", 
															cid=counter)
				# Get price
				price = await self.client_bridge.request(method_name="getprice", 
														cid=counter)
				# Get account public key
				account = await self.client_storage.request(method_name="getaccountbywallet",
														wallet=owneraddr["owneraddr"])
				public_key = account.get("public_key", None)
				# Append to contents list
				container.append({"cid":counter,"price": price,
									"owneraddr":owneraddr["owneraddr"],
									"public_key":public_key})
				counter = counter + 1
		self.write(json.dumps(container))

	def options(self):
		self.write(json.dumps(["GET"]))





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
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, OPTIONS')


	async def get(self, public_key=None):
		"""Returns content from blockchain
		Accepts:
			- hash or cid or (hash and cid)
		Returns:
			-  cid, hash and content
		"""
		# Check if public_key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
													public_key=public_key)
		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		# Get cid and hash
		cid = self.get_argument("cid", None)
		hash_ = self.get_argument("hash", None)
		# Check if any exists
		if not any([cid, hash_]):
			self.set_status(400)
			self.write({"error":400, 
						"reason":"Missed required fields"})
			raise tornado.web.Finish
		# Make requests to bridge
		if cid and str(cid).isdigit():
			owner = await self.client_bridge.request(method_name="ownerbycid", 
													cid=cid)
			data = await self.client_bridge.request(method_name="readbycid", 
													cid=cid)
			response = {"owner":owner.get("owneraddr", "Not found"),
						"data":data.get("hash", "Not found")}
		elif hash_:
			cid = await self.client_bridge.request(method_name="getcid", 
													hash=hash_)
			data = await self.client_bridge.request(method_name="ipfscat", 
													hash=hash_)
			owner = await self.client_bridge.request(method_name="ownerbycid", 
													cid=cid["cid"])
			response = {"cid":cid.get("cid"),"data":data.get("data"),
						"owner":owner.get("owneraddr")}
			if not cid["cid"]:
				response.update({"error": "Hash not found"})
		self.write(response)
		


	async def post(self, public_key=None):
		"""Writes content to blockchain

		Accepts:
			- cus (content)
			- public_key

		"""
		super().verify()
		# Check if public_key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
											public_key=public_key)

		if "error" in account.keys():
			self.set_status(account["error"])
			self.write(account)
			raise tornado.web.Finish

		# Get message from request 
		message = json.loads(self.get_body_argument("message", "{}"))
		if not message:
			self.set_status(403)
			self.write({"error":403, "reason":"Forbidden"})
			raise tornado.web.Finish
		# Overload data dictionary
		cus = message.get("cus", None)
		description = message.get("description", None)
		price = message.get("price", None)
		if not all([cus, description, price]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish
		# Send requests to bridge
		owneraddr = Qtum.public_key_to_hex_address(public_key)
		data = {"cus":cus, 
				"owneraddr":owneraddr, 
				"description":description, 
				"price":price
				}
		response = await self.client_bridge.request(method_name="makecid", **data)
		try:
			response["error"]
		except:
			self.set_status(400)
			self.write(response)
			raise tornado.web.Finish
		else:
			self.write(response)


	def options(self):
		self.write(json.dumps(["GET", "POST"]))



class DescriptionHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles blockchain content description requests
	"""


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, cid):
		"""Receives content description from blockchain
		"""
		# Get all parameters from request
		if not cid or not cid.isdigit():
			self.set_status(400)
			self.write({"error":400, 
					"reason":"Missed required fields or cid is not digit"})
			raise tornado.web.Finish

		# Send requests to bridge
		response = await self.client_bridge.request(method_name="descrbycid", cid=cid)
		logging.debug(response)
		self.write(response)


	async def post(self, cid):
		"""Set description for content
		"""
		super().verify()

		# Check if required fields exists
		public_key = self.get_body_argument("public_key", None)
		message = json.loads(self.get_body_argument("message", "{}"))
		cid = message.get("cid")
		descr = message.get("description")

		if not all([public_key, cid, descr]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish
		
		# Get content owner
		response = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		if "error" in response.keys():
			error_code = response["code"]
			self.set_status(error_code)
			self.write({"error":error_code, "reason":response["error"]})

		# Check if content owner has current public key 
		if not response["owneraddr"] == Qtum.public_key_to_hex_address(public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Owner does not match."})
		# Set description for content
		request = await self.client_bridge.request(method_name="setdescrforcid", 
						cid=cid, descr=descr, owneraddr=response["owneraddr"])
		if "error" in request.keys():
			self.set_status(request["error"])
			self.write(request)
			raise tornado.web.Finish
		self.write(request)


	def options(self):
		self.write(json.dumps(["GET", "POST"]))
	


class PriceHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles content price requests
	"""


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, OPTIONS')


	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	async def get(self, cid):
		"""Receives price for current cid

		Accepts:
			- cid
		"""
		price = await self.client_bridge.request(method_name="getprice", cid=cid)
		if not price:
			self.write({"error":404, "reason":"Price not found"})
		else:
			self.write({"price":price})


	async def post(self, cid):
		"""Sets price for blockchain content

		Accepts:
			- cid
			- owners public key
			- price
		""" 
		super().verify()
		
		message = json.loads(self.get_body_argument("message", "{}"))
		cid = message.get("cid", "")
		price = message.get("price", "")
		public_key = self.get_body_argument("public_key", "")
		
		if not all([public_key, str(cid).isdigit(), str(price).isdigit()]):
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish
		# Check if current public key is content owner
		response = await self.client_bridge.request(method_name="ownerbycid", cid=cid)

		if "error" in response.keys():
			self.set_status(404)
			self.write({"error":404, "reason":"Owner not found."})
			raise tornado.web.Finish

		if not response["owneraddr"] == Qtum.public_key_to_hex_address(public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Owner does not match."})
			raise tornado.web.Finish
		# Make setprice request to the bridge
		response = await self.client_bridge.request(method_name="setprice", 
								cid=cid, price=price, owneraddr=response["owneraddr"])
		self.write(response)

	def options(self):
		self.write(json.dumps(["GET", "POST"]))



class OfferHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles requests binded with offers (make, reject etc)
	"""
	def initialize(self, client_bridge, client_storage, client_balance, client_email):
		self.client_bridge = client_bridge
		self.client_storage = client_storage
		self.client_balance = client_balance
		self.client_email = client_email


	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, OPTIONS')


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
		
		message = json.loads(self.get_body_argument("message"))
		buyer_access_string = message.get("buyer_access_string")
		cid = message.get("cid")
		price = message.get("price")
		# Get cid price from bridge
		if not price:
			price = await self.client_bridge.request(method_name="getprice", cid=cid)
			
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

		# Check if current offer exists
		offer = await self.client_storage.request(method_name="getoffer",
			cid=cid, buyer_addr=Qtum.public_key_to_hex_address(public_key))
		if "cid" in offer.keys():
			self.set_status(403)
			self.write({"error":403,
						"reason":"Current offer already exists"})
			raise tornado.web.Finish

	
		#Get balance
		balance = await self.client_balance.request(method_name="getbalance", 
													uid=account["id"])
		#Detect owner
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", 
													cid=cid)
		owneraddr = owneraddr.get("owneraddr","")
		if owneraddr == Qtum.public_key_to_hex_address(public_key):
			self.set_status(400)
			self.write({"error":400, 
						"reason":"Content belongs to current user"})
			raise tornado.web.Finish
		# Get difference with balance and price
		difference = float(balance[str(account["id"])]) - float(price)
		if difference >= 0:

			
			# Make offer
			buyer_addr = Qtum.public_key_to_hex_address(public_key)
			offer_data = {
				"cid":cid,
				"price":price,
				"buyer_addr": buyer_addr,
				"buyer_access_string":buyer_access_string
			}
			response = await self.client_bridge.request(method_name="make_offer", 
														**offer_data)
			
			# Send appropriate mail to seller
			seller = await self.client_storage.request(method_name="getaccountbywallet",
												wallet=owneraddr)
			try:
				email = seller["email"]
			except:
				self.set_status(404)
				self.write({"error":404, 
							"reason":"Sellers account was not found"})
				raise tornado.web.Finish
			else:
				
				# Insert offer to the database
				await self.client_storage.request(method_name="insertoffer",
									cid=cid, price=price, buyer_addr=buyer_addr)

			self.write(response)
		else:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Insufficient funds"})
			raise tornado.web.Finish



	async def put(self, public_key=None):
		"""Reject offer

		Accepts:
			- cid
			- buyer public key
			- buyer address
		"""
		super().verify()
		
		# Check if message contains required data
		message = json.loads(self.get_body_argument("message", "{}"))
		logging.debug(message)
		try:
			cid = message["offer_id"]["cid"]
			buyer_addr = message["offer_id"]["buyer_addr"]
		except:
			self.set_status(400)
			self.write({"error":400, "reason":"Missed required fields"})
			raise tornado.web.Finish
		else:
			pass
		# Check if public key exists
		account = await self.client_storage.request(method_name="getaccountdata", 
										public_key=public_key)
		if "error" in account.keys():
			error_code = account["error"]
			self.set_status(error_code)
			self.write(account)
			raise tornado.web.Finish

		# Check if current offer exists
		offer = await self.client_storage.request(method_name="getoffer",
									cid=cid, buyer_addr=buyer_addr)
		if not "cid" in offer.keys():
			self.set_status(400)
			self.write({"error":400,
						"reason":"Current offer does not exist"})
			raise tornado.web.Finish
	
		# Check if one of seller or buyer rejects offer
		owneraddr = await self.client_bridge.request(method_name="ownerbycid", cid=cid)
		owneraddr = owneraddr.get("owneraddr","")
		hex_ = Qtum.public_key_to_hex_address(public_key)
		if buyer_addr == hex_ or owneraddr == hex_:
			# Reject offer
			response = await self.client_bridge.request(method_name="reject_offer",
											cid=cid, buyer_addr=buyer_addr)
			buyer = await self.client_storage.request(method_name="getaccountbywallet",
													wallet=buyer_addr)
			try:
				email = buyer["email"]
			except:
				self.set_status(404)
				self.write({"error":404, 
							"reason":"Buyers account was not found."})
				raise tornado.web.Finish
			else:
				emaildata = {
					"to": email,
					"subject": "Robin8 support",
         			"optional": "Your offer with cid %s was rejected." % cid
         	
				}
				#await self.client_email.request(method_name="sendmail", **emaildata)
				# Remove offer from database
				await self.client_storage.request(method_name="removeoffer",
								cid=cid, buyer_addr=buyer_addr)
			self.write(response)
		else:
			# Avoid rejecting offer
			self.set_status(403)
			self.write({"error": 403, "reason":"Forbidden"})


	def options(self):
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
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, PUT, OPTIONS')

	async def post(self, public_key=None):
		"""Accepting offer by buyer

		Function accepts:
			- cid
			- buyer access string
			- buyer public key
			- seller public key
		"""
		super().verify()
		# Check if message contains required data
		message = json.loads(self.get_body_argument("message"))
		buyer_access_string = message.get("buyer_access_string")
		cid = message.get("cid")
		buyer_pubkey = message.get("buyer_pubkey")

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
		owneraddr = owneraddr.get("owneraddr")
		if owneraddr != Qtum.public_key_to_hex_address(public_key):
			self.set_status(403)
			self.write({"error":403, "reason":"Forbidden"})
			raise tornado.web.Finish

		# Check if current offer exists
		offer = await self.client_storage.request(method_name="getoffer",
			cid=cid, buyer_addr=Qtum.public_key_to_hex_address(buyer_pubkey))

		if "error" in offer.keys():
			self.set_status(offer["error"])
			self.write(offer)
			raise tornado.web.Finish

		buyer_access_string = Qtum.to_compressed_public_key(buyer_access_string)

		#Get buyers balance
		balance = await self.client_balance.request(method_name="getbalance", 
										uid=buyer_account["id"])
		# Get difference with balance and price
		difference = float(balance[str(buyer_account["id"])]) - float(offer["price"])
		if difference >= 0:
			# Change content owner
			chownerdata = {
				"cid":cid,
				"new_owner": Qtum.public_key_to_hex_address(buyer_pubkey),
				"access_string": buyer_access_string
			}
			chown = await self.client_bridge.request(method_name="changeowner", 
													**chownerdata)
			if "error" in chown.keys():
				self.set_status(chown["error"])
				self.write(chown)
				raise tornado.web.Finish

			# Sellcontent
			selldata = {
				"cid":cid,
				"buyer_addr":Qtum.public_key_to_hex_address(buyer_pubkey),
				"access_string":buyer_access_string
			}
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
				await self.client_balance.request(method_name="decbalance", 
									uid=buyer_account["id"], amount=offer["price"])
				await self.client_balance.request(method_name="incbalance", 
									uid=seller_account["id"], amount=offer["price"])

				# Remove offer from database
				await self.client_storage.request(method_name="removeoffer",cid=cid,
						buyer_addr=Qtum.public_key_to_hex_address(buyer_pubkey))
				
				self.write({**sell, **chown})
				#self.write(sell)
		else:
			# If Insufficient funds
			self.set_status(402)
			self.write({"error":402, "reason":"Insufficient funds"})


	def options(self):
		self.write(json.dumps(["POST"]))
