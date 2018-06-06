import json
from jsonrpcserver.aio import methods
from jsonrpcclient.tornado_client import TornadoClient
import pymongo
from motor.motor_tornado import MotorClient
from pymongo import MongoClient
import tornado_components.mongo
import settings
import logging
from qtum_utils.qtum import Qtum




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
		logging.debug(response)
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
		

		if not account["news_count"]:
			return []

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
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		event_type = params.get("event_type", None)
		cid = params.get("cid", None)
		access_string = params.get("access_string", None)
		buyer_pubkey = params.get("buyer_pubkey", None)
		buyer_addr = params.get("buyer_addr", None)
		owneraddr = params.get("owneraddr", None)
		offer_price = params.get("offer_price", None)

		if not all([event_type, cid, access_string, offer_price, 
					buyer_pubkey, buyer_addr, owneraddr]):
			return {"error":400, "reason":"Missed required fields"}			

		# Get address of content owner and check if it exists
		client_bridge = TornadoClient(settings.bridgeurl)
		wallet = await client_bridge.request(method_name="ownerbycid",cid=cid)

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
		seller_price = await client_bridge.request(method_name="getprice", cid=cid)
		 
		try:
			row = {"event_type": event_type, 
					"buyer_addr":buyer_addr,
					"cid":cid,
					"access_string":access_string,
					"buyer_pubkey": buyer_pubkey,
					"seller_price": seller_price,
					"buyer_price": offer_price,
					"account_id": seller_account["id"]}
		except Exception as e:
			result = {"error":400, "reason":"Missed required fields.",
							"except": str(e)}
		else:
			# Update counter inside accounts table
			await accounts.find_one_and_update(
							{"id": seller_account["id"]},
							{"$inc": {"news_count": 1}})
			# Insert data to news table
			await news_collection.insert_one(row)

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
		buyer_addr = params.get("buyer_addr")
		price = params.get("price")
		txid = params.get("txid")
		owner_pubkey = params.get("owner_pubkey")
		owner_addr = params.get("owner_addr")
		# Check if required fileds 
		if not all([cid, buyer_addr, price, txid, owner_pubkey, owner_addr]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_addr})
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
		await offer_collection.insert_one({"confirmed":None,
						"account_id":wallet["account_id"], "owner_pubkey":owner_pubkey,
						"cid":cid, "buyer_price":price, 
						"txid":txid, "owner_addr":owner_addr})
		new_offer = await offer_collection.find_one({
						"account_id":wallet["account_id"],
						"cid":cid})
		return {i:new_offer[i] for i in new_offer if i != "_id"}
	

	async def get_offer(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
		cid = int(params.get("cid", 0))
		buyer_addr = params.get("buyer_addr")
		# Check if required fileds 
		if not all([cid, buyer_addr]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_addr})
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
				# Try to find offer with account id and cid
		offer_collection = self.database[settings.OFFER]
		offer = await offer_collection.find_one(
							{"account_id":wallet["account_id"],
							"cid":cid})
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
										"cid":cid,
										"confirmed":{"$ne":None}}):
				buyer = await self.collection.find_one({"id":document["account_id"]})
				cus = await content_collection.find_one({"cid":cid})
				document["seller_price"] = cus["price"]
				document["public_key"] = buyer["public_key"]
				del document["owner_pubkey"]
				del document["owner_addr"]
				document["buyer_address"] = Qtum.public_key_to_hex_address(document["public_key"])
				offers.append(document)
		else:
			async for document in offer_collection.find({
										"account_id":account["id"],
										"confirmed":{"$ne":None}}):
				content = await content_collection.find_one({"cid":document["cid"]})
				try:
					document["seller_price"] = content["price"]
					document["description"] = content["description"]
				except:
					continue
				offers.append(document)

		# Return list with offers
		return [{i:doc[i] for i in doc if i != "_id" and i != "txid"
							and i != "account_id" 
							and i != "confirmed"} for doc in list(offers)]


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
		buyer_addr = params.get("buyer_addr")
		# Check if required fileds 
		if not all([cid, buyer_addr]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_addr})
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
		flag = params.get("flag")
		# Check if required fileds 
		if not all([txid, flag]):
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
							{"txid":txid}, {"$set":{"confirmed":flag}})
		# Get updated offer
		updated = await offer_db.find_one({"txid":txid})

		return {i:updated[i] for i in updated if i != "_id"}


	async def mailed_confirm(self, **params):
		"""Receives offer data if exists

		Accepts:
			- cid
			- buyer address
		"""
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		# Check if required fields exists
		cid = params.get("cid")
		buyer_addr = params.get("buyer_addr")
		price = params.get("price")
		# Check if required fileds 
		if not all([cid, buyer_addr, price]):
			return {"error":400, "reason":"Missed required fields"}

		client_email = TornadoClient(settings.emailurl)
		client_bridge = TornadoClient(settings.bridgeurl)

		# Get content owner address
		owneraddr = await client_bridge.request(method_name="ownerbycid", cid=cid)
		# Send appropriate mail to seller
		wallets = self.database[settings.WALLET]
		seller = await wallets.find_one({"wallet":owneraddr["owneraddr"]})
		if not seller:
			return {"error":404,"error":"Not found current seller address"}
		accounts = self.database[settings.ACCOUNTS]
		seller_account = await accounts.find_one(
								{"id":seller["account_id"]})
		if not seller_account:
			return {"error":404, "error":"Not found current seller account"}

		emaildata = {
			"to": seller_account["email"],
			"subject": "Robin8 support",
 			"optional": "You`ve got a new offer from %s" % seller_account["public_key"]
 	
		}
		#await client_email.request(method_name="sendmail", **emaildata)

		# Leave news for seller
		buyer = await wallets.find_one({"wallet":buyer_addr})
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
			"buyer_addr":buyer_addr,
			"owneraddr":owneraddr["owneraddr"],
			"offer_price": price
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
		async for document in content_collection.find({"account_id":account["id"], 
														"cid":{"$ne":None}}):
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
		price = int(params.get("price", 0))
		description = params.get("description")
		content = params.get("content")

		if not all([content, account_id, txid]):
			return {"error":400, "reason":"Missed content field"}
		# Try to get account
		account = await self.collection.find_one({"id":account_id})
		# Return error if does not exist the one
		if not account:
			return {"error":404, "reason":"Account was not found"}

		content_collection = self.database[settings.CONTENT]
		await content_collection.insert_one({
								"account_id": account_id, "description":description,
								"price":price, "content":content, "cid":None,
								"txid": txid
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

		txid = params.get("txid")
		cid = params.get("cid")

		if not all([txid, cid]):
			return {"error":400, "reason":"Missed required fields"}

		content_collection = self.database[settings.CONTENT]
	
		await content_collection.find_one_and_update(
								{"txid":params["txid"]}, 
									{"$set":{"cid":cid}})
 
		updated = await content_collection.find_one({
										"txid":txid
								})

		if not updated:
			return {"error":404, 
					"reason":"Content not found"}
		else:
			return {i:updated[i] for i in updated if i != "_id"}


	async def get_all_content(self):
		"""Retrieving all content
		"""
		content_collection = self.database[settings.CONTENT]
		contents = []
		async for document in content_collection.find({"cid":{"$ne":None}}):
			owner = await self.collection.find_one({"id":document["account_id"]})
			document["owner"] = owner["public_key"]
			contents.append(document)
		result = [{i:doc[i] for i in doc if i != "_id" and i != "txid"
							and i != "account_id" and i != "address" and i != "public_key"} 
														for doc in contents]
		return result





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