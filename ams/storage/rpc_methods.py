from jsonrpcserver.aio import methods
import pymongo
import tornado_components.mongo
import settings
import logging


class NewsTable(tornado_components.mongo.Table):
	"""Added method for retrieving last rows.
	"""

	def insert_cid(self, **params):
		"""Inserts content id to database (related to account)
		"""
		if not params:
			result = {"error":400, "reason":"Missed required fields"}

		account = self.collection.find_one({"public_key": params["public_key"]})
		# Set database connection
		cids_client = pymongo.MongoClient()
		cids_db = cids_client[settings.DBNAME]
		cids_collection = cids_db[settings.CID]

		data = {
			"account_id": account["id"],
			"cid": params["cid"]
		}
		# Create row
		cids_collection.insert_one(data)

		row = cids_collection.find_one({"cid":cid})

		if row:
			return {i:row[i] for i in row if i != "_id"}
		else:
			return {"error":500, 
					"reason":"Not created"}



	def find_recent_news(self, **params):
		"""Accepts account public key and returns
		amount of recent news for account.
		"""
		if not params:
			result = {"error":400, "reason":"Missed required fields"}
		#Get account by public key
		account = self.collection.find_one({"public_key": params["public_key"]})
		if account:
			#Get account id
			account_id = account["id"]
			#Get news amount for current account
			account_news_amount = account["news_count"]
		else:
			return {"error":404, "reason":"Not Found"}

		# Get news amount for current account from news collection
		# Connect to news collection
		news_client = pymongo.MongoClient()
		news_db = news_client[settings.DBNAME]
		news_collection = news_db[settings.NEWS]
		try:
			# Get news 
			result = news_collection.find({"account_id":account_id}
									).sort("{$natural: -1}").limit(
										account_news_amount)
		except Exception as e:
			logging.debug(str(e))
			return {"error":404, "reason":"Not Found"}
		else:
			# Set news amount to zero.
			self.collection.find_one_and_update(
							{"public_key": params["public_key"]},
							{"$set": {"news_count": 0}})
			return list(result)


	def insert_news(self, **params):
		"""
		Accepts fields:
			event_type, buyer_id, cid, access_string
		Return {"result":"ok"} or {"error":int(code), "reason":str(reason)}
		"""
		if not params:
			result = {"error":400, "reason":"Missed required fields"}
		#Get account by public key
		account = self.collection.find_one({"public_key": params["public_key"]})
		if account:
			#Get account id
			account_id = account["id"]
			#Get news amount for current account
			account_news_amount = account["news_count"]
		else:
			return {"error":404, "reason":"Not Found"}
		# Connect to news table 
		news = tornado_components.mongo.Table(dbname=settings.DBNAME,
											collection=settings.NEWS)
		news_client = pymongo.MongoClient()
		news_db = news.client[settings.DBNAME]
		news_collection = news_db[settings.NEWS]

		# Insert news to news collection
		# Update news amount at accounts collection
		try:
			row = {"account_id":account_id, "event_type": params["event_type"],
					"buyer_address": params["buyer_address"], "cid":params["cid"],
					"access_string":params["access_string"]}
		except:
			result = {"error":400, "reason":"Missed required fields."}
		else:
			# Update counter inside accounts table
			self.collection.find_one_and_update(
							{"public_key": params["public_key"]},
							{"$inc": {"news_count": 1}})
			# Insert data to news table
			news_collection.insert_one(row)
			result = {"result":"ok"}
		return result



table = NewsTable(dbname=settings.DBNAME, collection=settings.COLLECTION)


@methods.add
async def createaccount(**params):
	document = table.insert(**params)
	return {i:document[i] for i in document if i != "_id"}


@methods.add
async def getnews(**params):
	news = table.find_recent_news(**params)
	result = [{i:j[i] for i in j if i != "_id"} for j in news]
	return result
	#return {i:news[i] for i in news if i != "_id"}


@methods.add 
async def setnews(**params):
	result = table.insert_news(**params)
	return result


@methods.add
async def getaccountdata(**params):
	document = table.find(**params)
	return {i:document[i] for i in document if i != "_id"}


@methods.add
async def addcid(**params):
	document = table.insert_cid(**params)
	return {i:document[i] for i in document if i != "_id"}

