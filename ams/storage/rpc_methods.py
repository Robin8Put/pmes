from jsonrpcserver.aio import methods
from jsonrpcclient.http_client import HTTPClient
import pymongo
from motor.motor_tornado import MotorClient
import tornado_components.mongo
import settings
import logging




class NewsTable(tornado_components.mongo.Table):
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
		wallet_client = MotorClient()
		wallet_db = wallet_client[settings.DBNAME]
		wallet_collection = wallet_db[settings.WALLET]

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
		news_client = pymongo.MongoClient()
		news_db = news_client[settings.DBNAME]
		news_collection = news_db[settings.NEWS]
		

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
		if not params:
			return {"error":400, "reason":"Missed required fields"}
		event_type = params.get("event_type", None)
		cid = params.get("cid", None)
		access_string = params.get("access_string", None)
		buyer_pubkey = params.get("buyer_pubkey", None)
		buyer_addr = params.get("buyer_addr", None)
		owneraddr = params.get("owneraddr", None)

		logging.debug("[+] -- Insert news debugging")
		logging.debug(params)
		if not all([event_type, cid, access_string, buyer_pubkey, buyer_addr, owneraddr]):
			return {"error":400, "reason":"Missed required fields"}			


		# Get address of content owner and check if it exists
		bridge_client = HTTPClient(settings.bridgeurl)
		wallet = bridge_client.request(method_name="ownerbycid",cid=cid)
		#Get account by wallet
		wallet_client = MotorClient()
		wallet_db = wallet_client[settings.DBNAME]
		wallet_collection = wallet_db[settings.WALLET]
		wallet = await wallet_collection.find_one({"wallet": owneraddr})
		if not wallet:
			return {"error":404,"reason":"Content owner not found"}
		account = await self.collection.find_one({"id":wallet["account_id"]})
		# Check if current public_key does exist in database
		buyeraccount = await self.collection.find_one({"public_key": buyer_pubkey})
		if not buyeraccount:
			return {"error":404,"reason":"Buyer not found"}
		
		# Connect to news table 
		news_client = MotorClient()
		news_db = news_client[settings.DBNAME]
		news_collection = news_db[settings.NEWS]
		logging.debug(account)
		# Insert news to news collection
		# Update news amount at accounts collection
		try:
			row = {"event_type": event_type, 
					"buyer_addr":buyer_addr,
					"cid":cid,
					"access_string":access_string,
					"buyer_pubkey": buyer_pubkey,
					"account_id": account["id"]}
		except:
			result = {"error":400, "reason":"Missed required fields."}
		else:
			# Update counter inside accounts table
			await self.collection.find_one_and_update(
							{"id": account["id"]},
							{"$inc": {"news_count": 1}})
			# Insert data to news table
			await news_collection.insert_one(row)

			result = {"result":"ok"}
		return result



table = NewsTable(dbname=settings.DBNAME, collection=settings.ACCOUNTS)


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
	wallettable = NewsTable(dbname=settings.DBNAME, 
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


