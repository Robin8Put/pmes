from jsonrpcserver.aio import methods
from jsonrpcclient.tornado_client import TornadoClient
import pymongo
from motor.motor_tornado import MotorClient
import tornado_components.mongo
import settings
import logging




class StorageTable(tornado_components.mongo.Table):
	"""Added method for retrieving last rows.
	"""

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


		account = await self.collection.find_one({"public_key": params["public_key"]})

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
		
		news_collection = self.database[settings.NEWS]
		

		if not account["news_count"]:
			return []
		limit = account["news_count"]
		# Get last "news_count" news from database
		news = news_collection.find({"account_id":account["id"]}
								).sort([("$natural", -1)]).limit(limit)
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
		logging.debug("[+] -- Logging news inserting")
		logging.debug(params)
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
		account = await self.collection.find_one({"id":wallet["account_id"]})
		# Check if current public_key does exist in database
		buyeraccount = await self.collection.find_one({"public_key": buyer_pubkey})
		if not buyeraccount:
			return {"error":404,"reason":"Buyer not found"}
		
		# Connect to news table 
		
		news_collection = self.database[settings.NEWS]
		# Insert news to news collection
		# Update news amount at accounts collection
		

		offer_collection = self.database[settings.OFFER]
		buyer_price = await offer_collection.find_one({
									"cid": cid, 
									"account_id":buyeraccount["id"]}) 
		logging.debug(cid)
		logging.debug(buyeraccount["id"])
		try:
			row = {"event_type": event_type, 
					"buyer_addr":buyer_addr,
					"cid":cid,
					"access_string":access_string,
					"buyer_pubkey": buyer_pubkey,
					"seller_price": offer_price,
					"buyer_price": buyer_price["price"]}
		except Exception as e:
			result = {"error":400, "reason":"Missed required fields.",
							"except": str(e)}
		else:
			# Update counter inside accounts table
			await self.collection.find_one_and_update(
							{"id": account["id"]},
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
							"cid":cid})
		# If current offer exists avoid creating a new one
		if offer:
			return {"error":403, "reason": "Current offer already exists"}
		# Else write a new offer to database
		await offer_collection.insert_one({"confirmed":None,
						"account_id":wallet["account_id"],
						"cid":cid, "price":price})
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
		offer = await offer_collection.find_one(
							{"account_id":wallet["account_id"],
							"cid":cid})
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
							"cid":cid})
		await offer_collection.delete_one(
							{"account_id":wallet["account_id"],
							"cid":cid})
		return {i:removed[i] for i in removed if i != "_id"}




table = StorageTable(dbname=settings.DBNAME, collection=settings.ACCOUNTS)


@methods.add
async def createaccount(**params):
	document = await table.insert(**params)
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



