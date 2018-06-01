import json
from jsonrpcserver.aio import methods
from jsonrpcclient.tornado_client import TornadoClient
import pymongo
from motor.motor_tornado import MotorClient
from pymongo import MongoClient
import tornado_components.mongo
import settings
import logging




class StorageTable(tornado_components.mongo.Table):
	"""Added method for retrieving last rows.
	"""

	async def create_account(self, **params):
		"""Describes, validates data.
		Calls create account method.
		"""
		model = {
		"unique": ["email", "public_key"],
		"required": ("public_key", "email", "device_id"),
		"default": {"count":1, "level":2, "news_count":0},
		"optional": ("phone",)}

		message = json.loads(params.get("message", "{}"))
		data = {**params, **message}
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
		else:
			# Reload data.
			row = {i:data[i] for i in data 
					if i in model["required"] or i in model["optional"]}
			row.update({i:model["default"][i] for i in model["default"]})
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
		news = news_collection.find({"account_id":account["id"]}
								).sort([("$natural", -1)]).limit(
										account["news_count"])
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
		cid = params.get("cid")
		buyer_addr = params.get("buyer_addr")
		price = params.get("price")
		# Check if required fileds 
		if not all([cid, buyer_addr, price]):
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
							"cid":int(cid)})
		# If current offer exists avoid creating a new one
		if offer:
			return {"error":403, "reason": "Current offer already exists"}
		# Else write a new offer to database
		await offer_collection.insert_one({"confirmed":None,
						"account_id":wallet["account_id"],
						"cid":int(cid), "price":price})
		new_offer = await offer_collection.find_one({
						"account_id":wallet["account_id"],
						"cid":int(cid)})
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
		cid = params.get("cid")
		buyer_addr = params.get("buyer_addr")
		# Check if required fileds 
		if not all([cid, buyer_addr]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_addr})
		logging.debug(wallet)
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
				# Try to find offer with account id and cid
		offer_collection = self.database[settings.OFFER]
		offer = await offer_collection.find_one(
							{"account_id":wallet["account_id"],
							"cid":int(cid)})
		# If current offer exists avoid creating a new one
		if not offer:
			return {"error":404, "reason": "Current offer not found"}
		else:
			return {i:offer[i] for i in offer if i != "_id"}


	async def remove_offer(self, **params):
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
							"cid":int(cid)})
		await offer_collection.delete_one(
							{"account_id":wallet["account_id"],
							"cid":int(cid)})
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
		cid = params.get("cid")
		buyer_addr = params.get("buyer_addr")
		flag = params.get("flag")
		# Check if required fileds 
		if not all([cid, buyer_addr, flag]):
			return {"error":400, "reason":"Missed required fields"}
		# Get buyer address row from database
		wallet_collection = self.database[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet":buyer_addr})
		if not wallet:
			return {"error":404, "reason":"Buyer address not found"}
		# Try to find offer with account id and cid
		offer_db = self.database[settings.OFFER]
		offer = await offer_db.find_one(
							{"account_id":wallet["account_id"],
							"cid":int(cid)})
		if not offer:
			logging.debug(offer_db.find())
			return {"error":404, 
					"reason":"Offer with user id %s and cid %s not found" % (
										wallet["account_id"], cid) }
		# Update offer
		await offer_db.find_one_and_update(
							{"account_id":wallet["account_id"],
							"cid":int(cid)}, {"$set":{"confirmed":flag}})
		# Get updated offer
		updated = await offer_db.find_one(
							{"account_id":wallet["account_id"],
													"cid":int(cid)})
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
