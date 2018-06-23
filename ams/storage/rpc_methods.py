import json
from jsonrpcserver.aio import methods
from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import SignedTornadoClient
import pymongo
from motor.motor_tornado import MotorClient
from pymongo import MongoClient
import tornado_components.mongo
import settings
import logging
from qtum_utils.qtum import Qtum


client_bridge = SignedTornadoClient(settings.bridgeurl)
client_email = TornadoClient(settings.emailurl)





class StorageTable(tornado_components.mongo.Table):
	"""Added method for retrieving last rows.
	"""

	async def create_account(self, **params):
		"""Describes, validates data.
		Calls create account method.
		"""
		model = {
		"unique": ["email", "public_key"],
		"required": ("public_key", "device_id"),
		"default": {"count":1, "level":2, "news_count":0, "email":None},
		"optional": ("phone",)}
		message = params.get("message", "{}")
		if isinstance(message, dict):
			data = {**params, **message}
		elif isinstance(message, str):
			data = {**json.loads(message), **params}
		# check if all required
		required = all([True if i in data.keys() else False for i in model["required"]])

		if not required:
			return {"error": 400,
					"reason":"Missed required fields"}

		# Unique constraint
		get_account = await self.collection.find_one({"public_key":data.get("public_key")})
		#get_account = await client.request(method_name="getaccountdata",
		#							public_key=data["public_key"])

		# Try get account with current public key
		if get_account:
			return {"error": 400,
					"reason": "Unique violation error"}
		# Reload data.
		row = {i:data[i] for i in data 
				if i in model["required"] or i in model["optional"]}
		row.update({i:model["default"][i] for i in model["default"]})
		if data.get("email"):
			row["email"] = data.get("email")
		row.update({"id":await self.autoincrement()})
		await self.collection.insert_one(row)
		response = await self.collection.find_one({"public_key":row["public_key"]})
		return response


	async def insert_wallet(self, **params):
		"""Inserts wallet to database (related to account)

		Accepts:
			- public_key
			- wallet
		Returns:
			- new row as dict
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		if not all([params.get("public_key"), params.get("wallet")]):
			return {"error":400, "reason":"Missed required fields"}
		accounts = self.database[settings.ACCOUNTS]
		account = await accounts.find_one({"public_key": params["public_key"]})

		# Set database connection
		
		wallet_collection = self.database[settings.WALLET]

		data = {
			"account_id": account["id"],
			"wallet": params["wallet"]
		}
		# Create row
		await wallet_collection.insert_one(data)
		# Get just created wallet
		row = await wallet_collection.find_one({"wallet":params["wallet"]})

		return row



	async def find_recent_news(self, **params):
		"""Looking up recent news for account.

		Accepts:
			- public_key
		Returns:
			- list with dicts or empty
		"""
		# Check if params is not empty
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required parameter does exist
		public_key = params.get("public_key", None)
		if not public_key:
			return {"error":400, "reason":"Missed required fields"}
		# Check if current public_key does exist in database
		account = await self.collection.find_one({"public_key": public_key})
		if not account:
			return {"error":404, "reason":"Current user not found"}

		
		# Connect to news collection
		client = MongoClient()
		news_db = client[settings.DBNAME]
		news_collection = news_db[settings.NEWS]
		
		# Get last "news_count" news from database
		#news = news_collection.find({"account_id":account["id"]}
		#						).sort([("$natural", -1)]).limit(
		#								account["news_count"])
		news = news_collection.find({"account_id":account["id"]}
								).sort([("$natural", -1)])
		
		# remove from result "_id" field	
		result = [{i:j[i] for i in j if i != "_id"} for j in news]
		
		# Set news amount to zero.
		await self.collection.find_one_and_update(
						{"public_key": params["public_key"]},
						{"$set": {"news_count": 0}})
		return result



	async def insert_news(self, **params):
		"""Inserts news for account

		Accepts:
			- event_type
			- cid
			- access_string (of buyer)
			- buyer_pubkey
		Returns:
			- dict with result
		"""
		logging.debug("[+] -- Insert news debugging")
		logging.debug("\n" + json.dumps(params) + "\n")
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		event_type = params.get("event_type", None)
		cid = params.get("cid", None)
		access_string = params.get("access_string", None)
		buyer_pubkey = params.get("buyer_pubkey", None)
		buyer_address = params.get("buyer_address", None)
		owneraddr = params.get("owneraddr", None)
		price = params.get("price", None)
		offer_type = int(params.get("offer_type", -1))

		if not all([event_type, cid, access_string, price, 
					buyer_pubkey, buyer_address, owneraddr]):
			return {"error":400, "reason":"Missed required fields"}			

		# Get address of content owner and check if it exists
		#client_bridge = TornadoClient(settings.bridgeurl)
		#wallet = await client_bridge.request(method_name="ownerbycid",cid=cid)

		#Get account by wallet
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet": owneraddr})
		if not wallet:
			return {"error":404,"reason":"Content owner not found"}

		# Check if seller account exists
		accounts = self.database[settings.ACCOUNTS]
		seller_account = await accounts.find_one({"id":wallet["account_id"]})
		if not seller_account:
			return {"error":404, "reason":"Seller not found"}

		# Check if current public_key does exist in database
		buyeraccount = await accounts.find_one({"public_key": buyer_pubkey})
		if not buyeraccount:
			return {"error":404,"reason":"Buyer not found"}
		
		# Connect to news table 
		news_collection = self.database[settings.NEWS]
		# Insert news to news collection
		# Update news amount at accounts collection
		content_collection = self.database[settings.CONTENT]
		content = await content_collection.find_one({"cid":int(cid)})

		identify = {0: "read_access", 1: "write_access"}

		
		row = {"offer_type": identify[offer_type], 
				"buyer_address":buyer_address,
				"cid":cid,
				"access_string":access_string,
				"buyer_pubkey": buyer_pubkey,
				"seller_price": content[identify[offer_type]],
				"buyer_price": price,
				"account_id": seller_account["id"]}

		logging.debug("\n" + json.dumps(row) + "\n")

		
		# Update counter inside accounts table
		await accounts.find_one_and_update(
						{"id": seller_account["id"]},
						{"$inc": {"news_count": 1}})
		# Insert data to news table
		await news_collection.insert_one(row)
		new = await news_collection.find_one({"cid":row["cid"]})

		result = {"result":"ok"}
		return result


	async def insert_offer(self, **params):
		"""Inserts new offer to database (related to buyers account)

		Accepts:
			- cid
			- buyer address
			- price
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
		cid = int(params.get("cid", 0))
		buyer_address = params.get("buyer_address")
		price = params.get("price")
		access_type = params.get("access_type")
		txid = params.get("txid")
		owner_pubkey = params.get("owner_pubkey")
		owner_addr = params.get("owner_addr")
		point = params.get("point")


		# Check if required fileds 
		if not all([cid, buyer_address, txid, owner_pubkey, owner_addr]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_address})
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
		# Try to find offer with account id and cid
		offer_collection = self.database[settings.OFFER]
		offer = await offer_collection.find_one(
							{"account_id":wallet["account_id"],
							"cid":cid})
		# If current offer exists avoid creating a new one
		if offer:
			return {"error":403, "reason": "Current offer already exists"}
		# Else write a new offer to database
		data = {"account_id":wallet["account_id"], 
				"owner_pubkey":owner_pubkey,
				"cid":cid, 
				"access_type":access_type,
				"txid":txid, 
				"owner_addr":owner_addr,
				"price":price,
				"confirmed": None}

		await offer_collection.insert_one(data)
		new_offer = await offer_collection.find_one({
						"account_id":wallet["account_id"],
						"cid":cid})
		return {i:new_offer[i] for i in new_offer if i != "_id"}
	

	ident_offers = {0: "read_access", 1: "write_access"}

	async def get_offer(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		logging.debug("[+] -- Get offer debugging")
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		logging.debug(params)
		# Check if required fields exists
		cid = int(params.get("cid", 0))
		#logging.debug(cid)
		buyer_address = params.get("buyer_address")
		#logging.debug(buyer_address)
		# Check if required fileds 
		if not all([cid, buyer_address]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_address})
		#logging.debug(wallet)
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
				# Try to find offer with account id and cid
		offer_collection = self.database[settings.OFFER]
		offer = await offer_collection.find_one(
							{"account_id":int(wallet["account_id"]),
							"cid":int(cid)})
		logging.debug(offer)
		# If current offer exists avoid creating a new one
		if not offer:
			return {"error":404, "reason": "Current offer not found"}
		else:
			return {i:offer[i] for i in offer if i != "_id"}


	async def get_offers(self, **params):
		"""Receives all users offers

		Accetpts:
		- public key
		"""
		logging.debug("[+] -- Get offers debugging")
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		cid = params.get("cid")
		public_key = params.get("public_key")
	
		# Try to get an account
		account = await self.collection.find_one({"public_key":public_key})
		logging.debug(account)
		# If does not exist - exit
		if not account:
			return {"error":404, "reason":"Account was not found"}
		# Get all offers
		content_collection = self.database[settings.CONTENT]
		offer_collection = self.database[settings.OFFER]
		offers = []
		if cid:
			cid = int(cid)
			async for document in offer_collection.find({
										"cid":cid}):
				buyer = await self.collection.find_one({"id":document["account_id"]})
				cus = await content_collection.find_one({"cid":int(cid)})
				document["public_key"] = buyer["public_key"]
				del document["owner_pubkey"]
				del document["owner_addr"]
				document["buyer_address"] = Qtum.public_key_to_hex_address(document["public_key"])
				offers.append(document)
		else:
			async for document in offer_collection.find({
										"account_id":account["id"]}):
				content = await content_collection.find_one({"cid":int(document["cid"])})
				try:
					document["description"] = content["description"]
				except:
					continue
				offers.append(document)

		# Return list with offers
		return [{i:doc[i] for i in doc if i != "_id" and i != "txid"
							and i != "account_id"} for doc in list(offers)]


	async def remove_offer(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
		cid = int(params.get("cid", 0))
		buyer_address = params.get("buyer_address")
		# Check if required fileds 
		if not all([cid, buyer_address]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_address})
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
				# Try to find offer with account id and cid
		offer_collection = self.database[settings.OFFER]
		removed = await offer_collection.find_one(
							{"account_id":wallet["account_id"],
							"cid":cid})
		await offer_collection.delete_one(
							{"account_id":wallet["account_id"],
							"cid":cid})
		return {i:removed[i] for i in removed if i != "_id"}


	async def update_offer(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
	
		txid = params.get("txid")
		confirmed = params.get("confirmed")
		point = params.get("point")


		# Check if required fileds 
		if not all([txid, confirmed]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		offer_db = self.database[settings.OFFER]
		offer = await offer_db.find_one(
							{"txid":txid})
		if not offer:
			return {"error":404, 
					"reason":"Offer with txid %s not found" % txid }
		# Update offer
		await offer_db.find_one_and_update(
							{"txid":txid}, {"$set":{"confirmed":confirmed}})
		# Get updated offer
		updated = await offer_db.find_one({"txid":txid})

		return {i:updated[i] for i in updated if i != "_id"}


	async def mailed_confirm(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		logging.debug("[+] -- Writing news debugging")
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
		logging.debug("[+] -- get params")
		logging.debug(params)
		cid = params.get("cid")
		buyer_address = params.get("buyer_address")
		price = params.get("price")
		offer_type = params.get("offer_type")
		point = params.get("point")


		# Check if required fileds 
		if not all([cid, buyer_address, price]):
			return {"error":400, "reason":"Missed required fields"}


		# Get content owner address
		owneraddr = await client_bridge.request(method_name="ownerbycid", cid=cid)

		# Get content
		#content_collection = self.database[settings.CONTENT]
		#content = await content_collection.find_one({"cid":int(cid)})
		# Get account
		#accounts_collection = self.database[settings.ACCOUNTS]
		#seller_account = await accounts_collection.find_one(
		#							{"id":content["account_id"]})
		# Get owneraddr with content and account
		#wallet_collection = self.database[settings.WALLET]
		#owneraddr = await wallet_collection.find_one({"account_id": seller_account["id"]})

		# Send appropriate mail to seller
		wallets = self.database[settings.WALLET]
		seller = await wallets.find_one({"wallet":owneraddr})
		if not seller:
			return {"error":404,"error":"Not found current seller address"}
		accounts = self.database[settings.ACCOUNTS]
		seller_account = await accounts.find_one(
								{"id":seller["account_id"]})
		if not seller_account:
			return {"error":404, "error":"Not found current seller account"}

		if seller_account.get("email"):
			emaildata = {
				"to": seller_account["email"],
				"subject": "Robin8 support",
	 			"optional": "You`ve got a new offer from %s" % seller_account["public_key"]
	 	
			}
			await client_email.request(method_name="sendmail", **emaildata)

		# Leave news for seller
		buyer = await wallets.find_one({"wallet":buyer_address})
		try:
			buyer_pubkey = await accounts.find_one({"id":buyer["account_id"]})
		except TypeError:
			return {"error":404, "reason":"Current buyer not found"}  
		# Send news for seller
		newsdata = {
			"event_type":"made offer",
			"cid": cid,
			"access_string":buyer_pubkey["public_key"],
			"buyer_pubkey":buyer_pubkey["public_key"],
			"buyer_address":buyer_address,
			"owneraddr":owneraddr,
			"price": price,
			"offer_type": offer_type
		}
		news = await self.insert_news(**newsdata)
		return {"result":"ok"}


	async def get_contents(self, **params):
		"""Retrieves all users content
		Accepts:
		-public key
		"""
		if not params or not params.get("public_key"):
			return {"error":400, "reason":"Missed required fields"}

		# Try to get account
		account = await self.collection.find_one({"public_key":params["public_key"]})
		# Return error if does not exist the one
		if not account:
			return {"error":404, "reason":"Account was not found"}

		content_collection = self.database[settings.CONTENT]
		#contents = await content_collection.find({"account_id":account["id"]})
		contents = []
		async for document in content_collection.find({"account_id":account["id"]}):
			contents.append(document)

		result = [{i:doc[i] for i in doc if i != "_id" and i != "account_id"
				and i != "address" and i != "public_key" and i != "txid"} for doc in contents]
		return result


	async def set_contents(self, **params):
		"""Writes users content to database
		Writes users content to database
		Accepts:
		- public key (required)
		- content (required)
		- description
		- price
		- address
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		txid = params.get("txid")
		account_id = params.get("account_id")
		read_access = int(params.get("read_access", 0))
		write_access = int(params.get("write_access", 0))
		description = params.get("description")
		content = params.get("content")
		seller_pubkey = params.get("seller_pubkey")
		seller_access_string = params.get("seller_access_string")

		if not all([content, account_id, txid]):
			return {"error":400, "reason":"Missed required fields"}
		# Try to get account
		account = await self.collection.find_one({"id":account_id})
		# Return error if does not exist the one
		if not account:
			return {"error":404, "reason":"Account was not found"}

		content_collection = self.database[settings.CONTENT]
		await content_collection.insert_one({
								"confirmed": None,
								"account_id": account_id, 
								"description":description,
								"read_access":read_access, 
								"write_access":write_access, 
								"content":content, 
								"cid":None,
								"txid": txid, 
								"seller_pubkey":seller_pubkey,
								"seller_access_string":seller_access_string
						})
		success = await content_collection.find_one({"account_id":account["id"],
													"content":content})
		if not success:
			return {"error":500, "reason":"Error while writing content to database"}

		else:
			return {"result":"ok"}


	async def update_contents(self, **params):
		"""Updates users content row
		Accepts:
		- txid
		- cid
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		logging.debug("[+] -- Update users content")
		logging.debug(params)

		txid = params.get("txid")
		cid = params.get("cid")
		description = params.get("description")
		write_price = params.get("write_price")
		read_price = params.get("read_price")
		confirmed = params.get("confirmed")



		content_collection = self.database[settings.CONTENT]

		if cid:	
			await content_collection.find_one_and_update(
									{"txid":params["txid"]}, 
										{"$set":{"cid":cid}})
		if description:
			await content_collection.find_one_and_update(
						{"txid":params["txid"]}, 
							{"$set":{"description":description}})
		if write_price:
			await content_collection.find_one_and_update(
									{"txid":params["txid"]}, 
										{"$set":{"write_price":write_price}})
		if read_price:
			await content_collection.find_one_and_update(
									{"txid":params["txid"]}, 
										{"$set":{"read_price":read_price}})
		if confirmed:
			await content_collection.find_one_and_update(
									{"txid":params["txid"]}, 
										{"$set":{"confirmed":confirmed}})

		updated = await content_collection.find_one({
										"txid":txid
								})

		if not updated:
			return {"error":404, 
					"reason":"Content not found"}
		else:
			return {i:updated[i] for i in updated if i != "_id"}



	async def set_access_string(self, **params):
		"""
		"""
		cid = int(params.get("cid", "0"))
		seller_access_string = params.get("seller_access_string")
		seller_pubkey = params.get("seller_pubkey")
		logging.debug(params)
		content = await self.collection.find_one({"cid":cid})
		logging.debug(content)

		if not content:
			return {"error":404, "reason":"Content not found"}

		if not all([cid, seller_access_string, seller_pubkey]):
			return {"error":400, "reason":"Missed required fields"}

		await self.collection.find_one_and_update({"cid":cid},
						{"$set":{"seller_access_string":seller_access_string}})

		await self.collection.find_one_and_update({"cid":cid},
						{"$set":{"seller_pubkey":seller_pubkey}})
		content = await self.collection.find_one({"cid":cid})
		logging.debug(content)
		return {i:content[i] for i in content if i != "_id"}


	async def get_all_content(self):
		"""Retrieving all content
		"""
		logging.debug("[+] -- Get all content debugging")
		content_collection = self.database[settings.CONTENT]
		contents = []

		async for document in content_collection.find():
			try:
				owner = await self.collection.find_one({"id":int(document["account_id"])})
				document["owner"] = owner["public_key"]
				contents.append(document)
			except:
				continue
		result = [{i:doc[i] for i in doc if i != "_id" and i != "txid"
							and i != "account_id" and i != "address" and i != "public_key"} 
														for doc in contents]
		return result


	async def get_single_content(self, cid):
		"""Receives single content by content id
		"""
		if not str(cid).isdigit():
			return {"error": 400, "reason": "Not valid parameter"}

		content = await self.collection.find_one({"cid":int(cid)})

		if not content:
			return {"error":404, "reason":"Content was not found"}
		accounts_collection = self.database[settings.ACCOUNTS]
		account = await accounts_collection.find_one({"id":content["account_id"]})
		content["owner"] = account["public_key"]
		return {i:content[i] for i in content if i != "_id"}


	async def change_content_owner(self, **params):
		"""Updates account id
		"""
		logging.debug("[+] -- Change content owner debugging")
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		logging.debug(params)

		cid = params.get("cid", 0)
		logging.debug(cid)
		buyer_pubkey = params.get("buyer_pubkey")
		logging.debug(buyer_pubkey)
		if not all([cid, buyer_pubkey]):
			return {"error":400, "reason":"Missed required fields"}

		buyer = await self.collection.find_one({"public_key":buyer_pubkey})
		logging.debug(buyer)
		content_collection = self.database[settings.CONTENT]
		await content_collection.find_one_and_update({"cid": int(cid)},
											{"$set":{"account_id":buyer["id"]}})
		result = await content_collection.find_one({"cid":int(cid)})
		logging.debug(result)
		if result:
			return {i:result[i] for i in result if i != "_id"}
		else:
			return {"error":500, "reason":"Error while changing owner in database"}


	async def add_content_owner(self, **params):
		"""Updates account id
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = params.get("cid", 0)
		buyer_pubkey = params.get("buyer_pubkey")
		if not all([cid, buyer_pubkey]):
			return {"error":400, "reason":"Missed required fields"}

		buyer = await self.collection.find_one({"public_key":buyer_pubkey})
		content_collection = self.database[settings.CONTENT]
		await content_collection.find_one_and_update({"cid": int(cid)},
											{"$set":{"account_id":buyer["id"]}})
		result = await content_collection.find_one({"cid":int(cid)})
		if result:
			return {i:result[i] for i in result if i != "_id"}
		else:
			return {"error":500, "reason":"Error while changing owner in database"}


	async def get_reviews(self, **params):
		"""Receives all reviews by cid
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = params.get("cid", 0)
		if not cid:
			return {"error":400, "reason":"Missed cid"}

		reviews = []
		async for document in self.collection.find({"cid":int(cid)}):
			#if document["confirmed"]:
			reviews.append({i:document[i] for i in document if i != "_id"})
			#else:
			#	continue

		return reviews


	async def set_review(self, **params):
		"""Writes review for content
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = int(params.get("cid", 0))
		review = params.get("review")
		public_key = params.get("public_key")
		rating = params.get("rating")
		txid = params.get("txid")

		if not all([cid, review, public_key, rating]):
			return {"error":400, "reason":"Missed required fields"}
		# Get account
		accounts_collection = self.database[settings.ACCOUNTS]
		account = accounts_collection.find_one({"public_key":public_key})
		if not account:
			return {"error":404, "reason":"Not found current user"}
		# Get content
		content_collection = self.database[settings.CONTENT]
		content = content_collection.find_one({"cid":cid})
		if not content:
			return {"error":404, "reason":"Not found current content"}
		"""
		if content["seller_access_string"] and content["account_id"] == account["id"]:
			await self.collection.insert_one({"cid":cid, "rating":rating, "confirmed":None,
										"review":review, "public_key":public_key, "txid":txid})
			return {"result":"ok"}
		else:
			return {"error":403, "reason":"Forbidden for review"}
		"""
		await self.collection.insert_one({"cid":cid, "rating":rating, "confirmed":None,
							"review":review, "public_key":public_key, "txid":txid})
		return {"result":"ok"}


	async def update_review(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
	
		txid = params.get("txid")
		confirmed = params.get("confirmed")
		point = params.get("point")

		# Check if required fileds 
		if not all([txid, confirmed]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		review = await self.collection.find_one(
									{"txid":txid})
		if not review:
			return {"error":404, 
					"reason":"Review with txid %s not found" % txid }
		# Update offer
		await self.collection.find_one_and_update(
							{"txid":txid}, {"$set":{"confirmed":confirmed}})
		# Get updated offer
		updated = await self.collection.find_one({"txid":txid})

		return {i:updated[i] for i in updated if i != "_id"}



	async def write_deal(self, **params):
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = int(params.get("cid", 0))

		access_type = params.get("access_type")

		buyer = params.get("buyer")

		seller = params.get("seller")

		price = params.get("price")


		if not all([cid, access_type, buyer, seller, price]):
			return {"error":400, "reason":"Missed required fields"}

		await self.collection.insert_one({
				"cid":cid,
				"access_type": access_type,
				"buyer":buyer,
				"seller":seller,
				"price":price
			})
		result = await self.collection.find_one({"cid":cid, "buyer":buyer})

		return {i:result[i] for i in result if i != "_id"}


	async def get_deals(self, **params):
		"""
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		buyer = params.get("buyer")

		if not buyer:
			return {"error":400, "reason":"Missed public key"}

		deals = []
		async for document in self.collection.find({"buyer":buyer}):
			deals.append({i:document[i] for i in document if i != "_id"})

		return deals


	async def update_description(self, **params):

		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
	
		cid = params.get("cid")
		description = params.get("description")
		txid = params.get("txid")

		# Check if required fileds 
		if not all([cid, description, txid]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		content = await self.collection.find_one({"cid":int(cid)})
		if not content:
			return {"error":404, 
					"reason":"Content with cid %s not found" % cid }
		# Update offer
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"description":description}})
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"confirmed":None}})
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"txid":txid}})
		# Get updated offer
		updated = await self.collection.find_one({"cid":int(cid)})

		return {i:updated[i] for i in updated if i != "_id"}


	async def set_write_price(self, **params):

		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
	
		cid = params.get("cid")
		price = params.get("write_price")
		txid = params.get("txid")


		# Check if required fileds 
		if not all([cid, price, txid]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		content = await self.collection.find_one({"cid":int(cid)})
		if not content:
			return {"error":404, 
					"reason":"Content with cid %s not found" % cid }
		# Update offer
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"write_access":price}})
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"confirmed":None}})
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"txid":txid}})
		# Get updated offer
		updated = await self.collection.find_one({"cid":int(cid)})

		return {i:updated[i] for i in updated if i != "_id"}


	async def set_read_price(self, **params):

		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
	
		cid = params.get("cid")
		price = params.get("read_price")
		txid = params.get("txid")

		# Check if required fileds 
		if not all([cid, price, txid]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		content = await self.collection.find_one({"cid":int(cid)})
		if not content:
			return {"error":404, 
					"reason":"Content with cid %s not found" % cid }
		# Update offer
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"read_access":price}})
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"confirmed":None}})
		await self.collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"txid":txid}})
		# Get updated offer
		updated = await self.collection.find_one({"cid":int(cid)})

		return {i:updated[i] for i in updated if i != "_id"}




table = StorageTable(dbname=settings.DBNAME, collection=settings.ACCOUNTS)


@methods.add
async def createaccount(**params):
	document = await table.create_account(**params)
	return {i:document[i] for i in document if i != "_id"}


@methods.add
async def getaccountdata(**params):
	document = await table.find(**params)
	return {i:document[i] for i in document if i != "_id"}


@methods.add
async def createwallet(**params):
	document = await table.insert_wallet(**params)
	return {i:document[i] for i in document if i != "_id"}


@methods.add
async def getnews(**params):
	news = await table.find_recent_news(**params)
	return news

@methods.add 
async def setnews(**params):
	result = await table.insert_news(**params)
	return result

@methods.add 
async def getaccountbywallet(**params):
	wallettable = StorageTable(dbname=settings.DBNAME, 
							collection=settings.WALLET)
	wallet = await wallettable.find(**params)
	try:
		document = await table.find(**{"id":wallet["account_id"]})
	except:
		document = {"public_key":None}
	return {i:document[i] for i in document if i != "_id"}

@methods.add
async def updatelevel(**params):
	document = await table.find(**{"id":params["id"]})
	data = {"_id":document["id"],
			"level":params["level"]}
	updated = await table.update(**data)
	return {i:updated[i] for i in updated if i != "_id"}


@methods.add 
async def insertoffer(**params):
	offertable = StorageTable(dbname=settings.DBNAME,
							collection=settings.OFFER)
	result = await offertable.insert_offer(**params)
	return result

@methods.add 
async def getoffer(**params):
	offertable = StorageTable(dbname=settings.DBNAME,
						collection=settings.OFFER)
	result = await offertable.get_offer(**params)
	return result

@methods.add 
async def removeoffer(**params):
	offertable = StorageTable(dbname=settings.DBNAME,
						collection=settings.OFFER)
	result = await offertable.remove_offer(**params)
	return result

@methods.add 
async def updateoffer(**params):
	offertable = StorageTable(dbname=settings.DBNAME,
						collection=settings.OFFER)
	result = await offertable.update_offer(**params)
	return result

@methods.add 
async def mailedconfirm(**params):
	offertable = StorageTable(dbname=settings.DBNAME,
						collection=settings.OFFER)
	result = await offertable.mailed_confirm(**params)
	return result

@methods.add 
async def getoffers(**params):
	result = await table.get_offers(**params)
	return result

@methods.add 
async def getuserscontent(**params):
	result = await table.get_contents(**params)
	return result

@methods.add 
async def setuserscontent(**params):
	result = await table.set_contents(**params)
	return result

@methods.add 
async def updateuserscontent(**params):
	result = await table.update_contents(**params)
	return result

@methods.add 
async def getallcontent():
	result = await table.get_all_content()
	return result

@methods.add 
async def getsinglecontent(cid):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.CONTENT)
	result = await table.get_single_content(cid)
	return result

@methods.add 
async def changecontentowner(**params):
	result = await table.change_content_owner(**params)
	return result

@methods.add 
async def setaccessstring(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.CONTENT)
	result = await table.set_access_string(**params)
	return result

@methods.add 
async def getreviews(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.REVIEW)
	result = await table.get_reviews(**params)
	return result

@methods.add 
async def setreview(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.REVIEW)
	result = await table.set_review(**params)
	return result

@methods.add 
async def updatereview(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.REVIEW)
	result = await table.update_review(**params)
	return result

@methods.add 
async def writedeal(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.DEAL)
	result = await table.write_deal(**params)
	return result

@methods.add 
async def getdeals(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.DEAL)
	result = await table.get_deals(**params)
	return result

@methods.add 
async def updatedescription(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.CONTENT)
	result = await table.update_description(**params)
	return result

@methods.add 
async def setwriteprice(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.CONTENT)
	result = await table.set_write_price(**params)
	return result

@methods.add 
async def setreadprice(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.CONTENT)
	result = await table.set_read_price(**params)
	return result