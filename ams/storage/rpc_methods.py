# Buily-ins
import logging
import json
import os
# Third-party
from jsonrpcserver.aio import methods
from jsonrpcclient.tornado_client import TornadoClient
from motor.motor_tornado import MotorClient
from pymongo import MongoClient
import pymongo
# Local packages
import settings
from utils.tornado_components import mongo
from utils.qtum_utils.qtum import Qtum
from utils.tornado_components.web import SignedTornadoClient, RobustTornadoClient
from utils.bip32keys.r8_ethereum.r8_eth import R8_Ethereum
from utils.models.account import Account


client = MotorClient()


coin_ids = settings.AVAILABLE_COIN_ID + ["PUT"]

def verify(func):

	async def wrapper(*args, **kwargs):
		import settings
		# Keys.json is file with public and private keys at projects directory
		with open(os.path.join(settings.BASE_DIR, "keys.json")) as f:
			keys = json.load(f)

		pubkey = keys["pubkey"]

		message = kwargs.get("message")
		signature = kwargs.get("signature")
		try:
			flag = Qtum.verify_message(message, signature, pubkey)
		except:
			flag = None
		if not flag:
			result =  {"error":403, "reason":"Invalid signature"}
		else:
			result = await func(*args, **kwargs)
			return result
		return wrapper


class StorageTable(mongo.Table):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.account = Account()
	
	#@verify
	async def create_account(self, **params):
		"""Describes, validates data.
		"""
		model = {
		"unique": ["email", "public_key"],
		"required": ("public_key",),
		"default": {"count":len(settings.AVAILABLE_COIN_ID), 
					"level":2, 
					"news_count":0, 
					"email":None},
		"optional": ("phone",)}

		message = json.loads(params.get("message", "{}"))
	
		data = {**message.get("message"), "public_key":message["public_key"]}

		# check if all required
		required = all([True if i in data.keys() else False for i in model["required"]])

		if not required:
			return {"error": 400,
					"reason":"Missed required fields"}

		# Unique constraint
		get_account = await self.collection.find_one({"public_key":data.get("public_key")})

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
		account = await self.collection.find_one({"public_key":row["public_key"]})

		# Create wallets

		for coinid in settings.AVAILABLE_COIN_ID:
			database = client[coinid]
			wallet_collection = database[settings.WALLET]
			await wallet_collection.insert_one({
					"account_id": account["id"],
					"wallet": self.account.validator[coinid](account["public_key"]) 
				})
			wallet = await wallet_collection.find_one({
					"account_id": account["id"],
					"wallet": self.account.validator[coinid](account["public_key"]) 
				})

		return account


	#@verify
	async def find_recent_news(self, **params):
		"""Looking up recent news for account.
		Accepts:
			- public_key
		Returns:
			- list with dicts or empty
		"""
		# Check if params is not empty
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
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
		news_db = client[settings.DBNAME]
		news_collection = news_db[settings.NEWS]
		
		news = []

		async for document in news_collection.find(
			{"account_id":account["id"]}).sort([("$natural", -1)]):
			news.append({i:document[i] for i in document if i != "_id"})
		
		
		# Set news amount to zero.
		accounts_collection = news_db[settings.ACCOUNTS]
		await accounts_collection.find_one_and_update(
						{"public_key": params["public_key"]},
						{"$set": {"news_count": 0}})
		return news



	async def insert_news(self, **params):
		"""Inserts news for account
		Accepts:
			- event_type
			- cid
			- access_string (of buyer)
			- buyer_pubkey
			- buyer address
			- owner address
			- price
			- offer type
			- coin ID
		Returns:
			- dict with result
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		event_type = params.get("event_type")
		cid = params.get("cid")

		access_string = params.get("access_string")

		buyer_pubkey = params.get("buyer_pubkey")

		buyer_address = params.get("buyer_address")

		owneraddr = params.get("owneraddr")

		price = params.get("price")

		offer_type = int(params.get("offer_type", -1))

		coinid = params.get("coinid").upper()

		# Get address of content owner and check if it exists
		if coinid in settings.AVAILABLE_COIN_ID:
			self.account.blockchain.setendpoint(settings.bridges[coinid])
		else:
			return {"error":400, "reason": "Invalid coin ID"}

		owneraddr = await self.account.blockchain.ownerbycid(cid=cid)

		# Get sellers account
		seller = await getaccountbywallet(wallet=owneraddr)
		if "error" in seller.keys():
			return seller

		# Connect to news table 
		news_collection = self.database[settings.NEWS]

		# Get sellers price
		self.account.blockchain.setendpoint(settings.bridges[coinid])
		if offer_type == 1:
			seller_price = await self.account.blockchain.getwriteprice(cid=cid)
		elif offer_type == 0:
			seller_price = await self.account.blockchain.getreadprice(cid=cid)

		
		row = {"offer_type": self.account.ident_offer[offer_type], 
				"buyer_address":buyer_address,
				"cid":cid,
				"access_string":access_string,
				"buyer_pubkey": buyer_pubkey,
				"seller_price": seller_price,
				"buyer_price": price,
				"account_id": seller["id"],
				"event_type": event_type,
				"coinid":coinid}
		
		# Update counter inside accounts table
		database = client[settings.DBNAME]
		collection = database[settings.ACCOUNTS]
		await collection.find_one_and_update(
						{"id": int(seller["id"])},
						{"$inc": {"news_count": 1}})
		await collection.find_one({"id":int(seller["id"])})
		
		# Insert data to news table
		await news_collection.insert_one(row)

		return {"result":"ok"}


	#@verify
	async def insert_offer(self, **params):
		"""Inserts new offer to database (related to buyers account)
		Accepts:
			- cid
			- buyer address
			- price
			- access type
			- transaction id
			- owner public key
			- owner address
			- coin ID
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = int(params.get("cid", 0))
		txid = params.get("txid")
		coinid = params.get("coinid")
		public_key = params.get("public_key")

		database = client[coinid]
		offer_collection = database[settings.OFFER]
		await offer_collection.insert_one({"cid":cid, "txid":txid, 
											"confirmed":None, "coinid":coinid, 
											"public_key":public_key})

		return {"result":"ok"}
	



	#@verify
	async def get_offer(self, **params):
		"""Receives offer data if exists
		Accepts:
			- cid
			- buyer address
			- coin ID
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = int(params.get("cid", 0))
		coinid = params.get("coinid")
		buyer_address = params.get("buyer_address")
		
		# Check if required fileds 
		if not all([cid, buyer_address, coinid]):
			return {"error":400, "reason":"Missed required fields"}
		
		# Get buyer address row from database
		database = client[coinid]
		wallet_collection = database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_address})
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
		
		# Try to find offer with account id and cid
		offer_collection = database[settings.OFFER]
		offer = await offer_collection.find_one(
							{"account_id":int(wallet["account_id"]),
							"cid":int(cid)})

		# If current offer exists avoid creating a new one
		if not offer:
			return {"error":404, "reason": "Current offer not found"}
		else:
			offer["coinid"] = coinid
			return {i:offer[i] for i in offer if i != "_id"}


	#@verify
	async def get_offers(self, **params):
		"""Receives all users input (by cid) or output offers 
		Accepts:
		- public key
		- cid (optional)
		- coinid (optional)
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = params.get("cid")
		public_key = params.get("public_key")
		coinid = params.get("coinid")

		offers = []

		# Get all input offers by cid
		if cid and coinid:
			cid = int(cid)
			database = client[coinid]
			offer_collection = database[settings.OFFER]
			content_collection = database[settings.CONTENT]

			async for document in offer_collection.find({"cid":cid, "confirmed":None}):
				offers.append({i:document[i] for i in document if i == "confirmed"})

		# Get all output users offers
		elif not cid:
			database = client[coinid]
			offer_collection = database[settings.OFFER]
			async for document in offer_collection.find({"public_key":public_key, 
																"confirmed":None}):
				offers.append({i:document[i] for i in document if i == "confirmed"})


		# Return list with offers
		return offers


	#@verify
	async def remove_offer(self, **params):
		"""Receives offfer after have deal
		Accepts:
			- cid
			- buyer address
			- coin ID
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = int(params.get("cid", 0))
		buyer_address = params.get("buyer_address")
		coinid = params.get("coinid")
	
		# Check if required fileds 
		if not all([cid, buyer_address]):
			return {"error":400, "reason":"Missed required fields"}
		
		# Try to find offer with account id and cid	
		offer = await self.get_offer(cid=cid, buyer_address=buyer_address, coinid=coinid)
		if "error" in offer.keys():
			return offer

		# Remove offer
		database = client[coinid]
		offer_collection = database[settings.OFFER]
		await offer_collection.delete_one(
							{"account_id":offer["account_id"],
							"cid":cid})
		return {"result": "ok"}


	async def update_offer(self, **params):
		"""Updates offer after transaction confirmation
		Accepts:
			- transaction id
			- coinid
			- confirmed (boolean flag)
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		txid = params.get("txid")
		coinid = params.get("coinid").upper()


		# Try to find offer with account id and cid
		database = client[coinid]
		offer_db = database[settings.OFFER]
		offer = await offer_db.find_one({"txid":txid})
		if not offer:
			return {"error":404, 
					"reason":"Offer with txid %s not found" % txid }

		# Update offer
		await offer_db.find_one_and_update(
							{"txid":txid}, {"$set":{"confirmed":1}})

		# Get updated offer
		updated = await offer_db.find_one({"txid":txid})

		return {i:updated[i] for i in updated if i != "_id"}



	async def mailed_confirm(self, **params):
		"""Sends mail to user after offer receiveing
		Accepts:
			- cid
			- buyer address
			- price
			- offer_type
			- point
			- coinid
		"""
		logging.debug("[+] -- Mailed confirm")
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = params.get("cid")
		buyer_address = params.get("buyer_address")
		price = params.get("price")
		offer_type = params.get("offer_type")
		coinid = params.get("coinid").upper()
		logging.debug(params)
		# Check if required fileds 
		if not all([cid, buyer_address, price]):
			return {"error":400, "reason":"Missed required fields"}




		# Get content owner address
		#if coinid in settings.AVAILABLE_COIN_ID:
		#	client_bridge.endpoint = settings.bridges[coinid]
		#else:
		#	return {"error":400, "reason":"Invalid coin ID"}
		#owneraddr = await client_bridge.request(method_name="ownerbycid", cid=cid)


		# Send appropriate mail to seller if exists
		#seller = await getaccountbywallet(wallet=owneraddr)
		#logging.debug(seller)
		#if "error" in seller.keys():
		#	return seller
		#if seller.get("email"):
		#	emaildata = {
		#		"to": seller["email"],
		#		"subject": "Robin8 support",
	 	#		"optional": "You`ve got a new offer from %s" % seller["public_key"]
	 	#
		#	}
		#	await client_email.request(method_name="sendmail", **emaildata)

		# Send news for seller
		buyer = await getaccountbywallet(wallet=buyer_address) 
		logging.debug(buyer)
		if "error" in buyer.keys():
			buyer["public_key"] = None

		newsdata = {
			"event_type":"made offer",
			"cid": cid,
			"access_string":buyer["public_key"],
			"buyer_pubkey":buyer["public_key"],
			"buyer_address":buyer_address,
			#"owneraddr":owneraddr,
			"price": price,
			"offer_type": offer_type,
			"coinid":coinid
		}
		news = await self.insert_news(**newsdata)
		return {"result":"ok"}


	#@verify
	async def get_contents(self, **params):
		"""Retrieves all users content
		Accepts:
		-public key
		"""
		logging.debug("[+] -- Get contents")
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))

		if not params or not params.get("public_key"):
			return {"error":400, "reason":"Missed required fields"}

		# Try to get account
		account = await self.collection.find_one({"public_key":params["public_key"]})
		# Return error if does not exist the one
		if not account:
			return {"error":404, "reason":"Get contents. Not found account"}

		contents = {i:[] for i in settings.AVAILABLE_COIN_ID}
		for coinid in settings.AVAILABLE_COIN_ID:
			logging.debug(coinid)
			database = client[coinid]
			content_collection = database[settings.CONTENT]
			async for document in content_collection.find({"owner":account["public_key"]}):
				contents[coinid].append((document["cid"], document["txid"]))

		return contents


	#@verify
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
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		txid = params.get("txid")
		public_key = params.get("public_key")
		_hash = params.get("hash")
		coinid = params.get("coinid")
		access = params.get("access")
		cid = params.get("cid")

		# Try to get account
		account = await self.collection.find_one({"public_key":public_key})
		# Return error if does not exist the one
		if not account:
			return {"error":404, "reason":"Account was not found"}

		client = MotorClient()
		database = client[coinid]
		content_collection = database[access]
		await content_collection.insert_one({
								"owner": public_key,
								"cid":cid,
								"txid": txid, 
								"hash": _hash
						})
		success = await content_collection.find_one({"txid":txid})
		if not success:
			return {"error":500, "reason":"Error while writing content to database"}

		else:
			return {"result":"ok"}

	#@verify
	async def update_contents(self, **params):
		"""Updates users content row
		Accepts:
		- txid
		- cid
		- description
		- write_price
		- read_price
		- confirmed
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))

		if not params:
			return {"error":400, "reason":"Missed required fields"}

		txid = params.get("txid")

		coinid = params.get("coinid").upper()

		client = MotorClient()
		database = client[coinid]
		content_collection = database[settings.CONTENT]

		content = await content_collection.find_one({"txid":txid})

		if not content:
			return {"error":404, 
					"reason":"Update content. Content with txid %s not found" % txid}

		if content.get("hash"):
			self.account.blockchain.setendpoint(settings.bridges[coinid])
			cid = await self.account.blockchain.getcid(hash=content["hash"])

			await content_collection.find_one_and_update({"txid":txid}, {"$set":{"cid":int(cid)}})
			await content_collection.find_one_and_update({"txid":txid}, {"$set":{"hash":None}})


		updated = await content_collection.find_one({"txid":txid})

		return {i:updated[i] for i in updated if i != "_id"}


	#@verify
	async def set_access_string(self, **params):
		"""Writes content access string to database 
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))

		cid = int(params.get("cid", "0"))
		seller_access_string = params.get("seller_access_string")
		seller_pubkey = params.get("seller_pubkey")
		coinid = params.get("coinid")

		database = client[coinid]
		collection = database[settings.CONTENT]
		content = await collection.find_one({"cid":cid})

		if not content:
			return {"error":404, "reason":"Content not found"}

		if not all([cid, seller_access_string, seller_pubkey]):
			return {"error":400, "reason":"Missed required fields"}

		await collection.find_one_and_update({"cid":cid},
						{"$set":{"seller_access_string":seller_access_string}})

		await collection.find_one_and_update({"cid":cid},
						{"$set":{"seller_pubkey":seller_pubkey}})

		content = await collection.find_one({"cid":cid})
		return {i:content[i] for i in content if i != "_id"}



	#@verify
	async def get_reviews(self, **params):
		"""Receives all reviews by cid
		Accepts:
		- cid
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = params.get("cid", 0)
		coinid = params.get("coinid")
		if not cid and not coinid:
			return {"error":400, "reason":"Missed cid"}

		reviews = []
		database = client[coinid]
		collection = database[settings.REVIEW]
		async for document in collection.find({"confirmed":None, "cid":int(cid)}):
			reviews.append({i:document[i] for i in document if i == "confirmed"})

		return reviews


	#@verify
	async def set_review(self, **params):
		"""Writes review for content
		Accepts:
		- cid
		- review
		- public_key
		- rating
		- txid
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = int(params.get("cid", 0))
		txid = params.get("txid")
		coinid = params.get("coinid")
		
		# Get content
		database = client[coinid]
		content_collection = database[settings.CONTENT]
		content = await content_collection.find_one({"cid":cid})
		if not content:
			return {"error":404, "reason":"Not found current content"}

		database = client[coinid]
		review_collection = database[settings.REVIEW]		
		await review_collection.insert_one({"cid":cid, "confirmed":None, 
											"txid":txid, "coinid":coinid})
		return {"result":"ok"}



	async def update_review(self, **params):
		"""Update review after transaction confirmation
		Accepts:
			- txid
			- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		
		# Check if required fields exists
		txid = params.get("txid")
		coinid = params.get("coinid").upper()

		# Try to find offer with account id and cid
		database = client[coinid]
		collection = database[settings.REVIEW]
		review = await collection.find_one({"txid":txid})
		if not review:
			return {"error":404, 
					"reason":"Review with txid %s not found" % txid }
		
		# Update review
		await collection.find_one_and_update(
							{"txid":txid}, {"$set":{"confirmed":1}})
		
		# Get updated offer
		updated = await collection.find_one({"txid":txid})

		return {i:updated[i] for i in updated if i != "_id"}



	#@verify
	async def write_deal(self, **params):
		"""Writes deal to database
		Accepts:
		- cid
		- access_type
		- buyer public key
		- seller public key
		- price
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		cid = int(params.get("cid", 0))
		access_type = params.get("access_type")
		buyer = params.get("buyer")
		seller = params.get("seller")
		price = params.get("price")
		coinid = params.get("coinid")

		if not all([cid, access_type, buyer, seller, price]):
			return {"error":400, "reason":"Missed required fields"}

		database = client[coinid]
		collection = database[settings.DEAL]
		await collection.insert_one({
				"cid":cid,
				"access_type": access_type,
				"buyer":buyer,
				"seller":seller,
				"price":price,
				"coinid":coinid
			})
		result = await collection.find_one({"cid":cid, "buyer":buyer})

		return {i:result[i] for i in result if i != "_id"}



	#@verify
	async def update_description(self, **params):
		"""Set description to unconfirmed status
		after updating by user.
		Accepts:
		- cid
		- description
		- transaction id
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = params.get("cid")
		description = params.get("description")
		txid = params.get("txid")
		coinid = params.get("coinid")

		# Check if required fileds 
		if not all([cid, description, txid, coinid]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		database = client[coinid]
		collection = database[settings.CONTENT]
		content = await collection.find_one({"cid":int(cid)})
		if not content:
			return {"error":404, 
					"reason":"Content with cid %s not found" % cid }

		# Update offer
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"description":description}})
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"confirmed":None}})
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"txid":txid}})

		# Get updated offer
		updated = await collection.find_one({"cid":int(cid)})

		return {i:updated[i] for i in updated if i != "_id"}


	#@verify
	async def set_write_price(self, **params):
		"""Updates write access price of content
		Accespts:
		- cid
		- price
		- txid
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = params.get("cid")
		price = params.get("write_price")
		txid = params.get("txid")
		coinid = params.get("coinid")

		# Check if required fileds 
		if not all([cid, price, txid]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		database = client[coinid]
		collection = database[settings.CONTENT]

		# Check if content exists
		content = await collection.find_one({"cid":int(cid)})
		if not content:
			return {"error":404, 
					"reason":"Content with cid %s not found" % cid }

		# Update content
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"write_access":price}})
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"confirmed":None}})
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"txid":txid}})
		# Get updated content
		updated = await collection.find_one({"cid":int(cid)})

		return {i:updated[i] for i in updated if i != "_id"}


	#@verify
	async def set_read_price(self, **params):
		"""Updates write access price of content
		Accespts:
		- cid
		- price
		- txid
		- coinid
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))

		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Check if required fields exists
		cid = params.get("cid")
		price = params.get("read_price")
		txid = params.get("txid")
		coinid = params.get("coinid")

		# Check if required fileds 
		if not all([cid, price, txid]):
			return {"error":400, "reason":"Missed required fields"}

		# Try to find offer with account id and cid
		database = client[coinid]
		collection = database[settings.CONTENT]

		# Check if content exists
		content = await collection.find_one({"cid":int(cid)})
		if not content:
			return {"error":404, 
					"reason":"Content with cid %s not found" % cid }
		
		# Update content
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"read_access":price}})
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"confirmed":None}})
		await collection.find_one_and_update(
							{"cid":int(cid)}, {"$set":{"txid":txid}})
		
		# Get updated content
		updated = await collection.find_one({"cid":int(cid)})

		return {i:updated[i] for i in updated if i != "_id"}


	async def change_owner(self, **params):
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))

		if not params:
			return {"error":400, "reason":"Missed required fields"}

		coinid = params.get("coinid")
		cid = params.get("cid")
		public_key = params.get("public_key")

		client = MotorClient()
		database = client[coinid]
		content_collection = database[settings.CONTENT]

		content = await content_collection.find_one_and_update({"cid":int(cid)}, 
										{"$set":{"owner":public_key}})

		if not content:
			return {"error":404, "reason":"Change owner. Content with cid %s not found" % cid}

		return {i:content[i] for i in content if i != "_id"}


	async def share_content(self, **params):
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))

		if not params:
			return {"error":400, "reason":"Missed required fields"}
		coinid = params.get("coinid")
		cid = params.get("cid")
		public_key = params.get("public_key")

		client = MotorClient()
		database = client[coinid]
		content_collection = database[settings.DEAL]

		await content_collection.insert_one({"cid":int(cid), "user":public_key})
		content = await content_collection.find_one({"cid":int(cid), "user":public_key})
		logging.debug(content)
		if not content:
			return {"error":404, 
					"reason":"Shared content. Content with cid %s not created" % cid}

		return {i:content[i] for i in content if i != "_id"}


	#@verify
	async def get_deals(self, **params):
		"""Receives all users deals
		Accepts:
		- buyer public key
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		buyer = params.get("buyer")

		if not buyer:
			return {"error":400, "reason":"Missed public key"}

		deals = {i:[] for i in settings.AVAILABLE_COIN_ID}
		client = MotorClient()
		for coinid in settings.AVAILABLE_COIN_ID:
			database = client[coinid]
			collection = database[settings.DEAL]
			async for document in collection.find({"owner":buyer}):
				deals[coinid].append((document["cid"],document.get("txid")))

		return deals


	async def log_source(self, **params):
		""" Logging users request sources
		"""
		if params.get("message"):
			params = json.loads(params.get("message", "{}"))
		
		if not params:
			return {"error":400, "reason":"Missed required fields"}

		# Insert new source if does not exists the one
		client = MotorClient()
		database = client[settings.DBNAME]
		source_collection = database[settings.SOURCE]
		await source_collection.update({"public_key":params.get("public_key")}, 
						 {"$addToSet":{"source":params.get("source")}},
						 upsert=True)

		return {"result": "ok"}




table = StorageTable(dbname=settings.DBNAME, collection=settings.ACCOUNTS)


@methods.add
async def createaccount(**params):
	document = await table.create_account(**params)
	return {i:document[i] for i in document if i != "_id"}


@methods.add
async def getaccountdata(**params):
	if isinstance(params.get("message"), str):
		params = json.loads(params.get("message", "{}"))
	elif isinstance(params.get("message"), dict):
		params = params.get("message")
	data = {i:params[i] for i in params if i == "public_key" or i == "id"}
	document = await table.find(**data)
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
	"""Receives account by wallet
	Accepts:
	- public key hex or checksum format
	"""
	if params.get("message"):
		params = json.loads(params.get("message"))

	for coinid in coin_ids:
		logging.debug("\n" + coinid + "\n")
		database = client[coinid]
		wallet_collection = database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":params["wallet"]})
		if not wallet:
			continue
		else:
			database = client[settings.DBNAME]
			accounts_collection = database[settings.ACCOUNTS]
			account = await accounts_collection.find_one({"id":wallet["account_id"]})
			if not account:
				return {"error":404, "reason":"Account was not found"}
			return {i:account[i] for i in account if i != "_id"}
	else:
		return {"error":404, "reason":"Account was not found"}


@methods.add
async def updatelevel(**params):
	message = json.loads(params.get("message"))
	document = await table.find(**{"id":message["id"]})
	data = {"_id":document["id"],
			"level":message["level"]}
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
async def getallcontent(**params):
	result = await table.get_all_content(**params)
	return result

@methods.add 
async def getsinglecontent(**params):
	table = StorageTable(dbname=settings.DBNAME, collection=settings.CONTENT)
	result = await table.get_single_content(**params)
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

@methods.add 
async def changeowner(**params):
	result = await table.change_owner(**params)
	return result

@methods.add 
async def sharecontent(**params):
	result = await table.share_content(**params)
	return result

@methods.add 
async def logsource(**params):
	result = await table.log_source(**params)
	return result