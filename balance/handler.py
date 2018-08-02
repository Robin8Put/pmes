# Built-ins
import os
import json
import sys
import logging
import bson

# Third-party
from motor.motor_tornado import MotorClient
from jsonrpcserver.aio import methods
import settings

# Locals
from utils.models.account import Account


def verify(func):
    async def wrapper(*args, **kwargs):
        import settings
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


class Abstract(object):
	""" Defines:
		- database name
		- collection name
		- autoincrement field
		- data validatation function
	"""

	def __init__(self):
		# Set database parameters

		self.client = MotorClient()

		self.collection = settings.BALANCE

		self.types = settings.AVAILABLE_COIN_ID

		self.account = Account()


	def error_403(self, reason):
		return {"error": 403, "reason":"Balance service. " + reason}

	def error_400(self, reason):
		return {"error": 400, "reason":"Balance service. " + reason}

	def error_404(self, reason):
		return {"error": 404, "reason":"Balance service. " + reason}


	async def autoincrement(*args):
		"""
		Adding autoincrement field to mongo collection
		"""

		collection = self.database.autoincrement

		counter = await collection.find_one({"name":"counter"})

		if not counter:
			await collection.insert_one({"name":"counter", "id": 0})

		await collection.find_one_and_update(
							{"name": "counter"},
							{"$inc": {"id": 1}})
		counter = await collection.find_one({"name":"counter"})
		return counter["id"]


	def validate(self, *args, **kwargs):

		if not kwargs:
			self.error_400("Validate. Missed parameters.")
			return

		message = kwargs.get("message")

		if message and isinstance(message, str):
			kwargs = json.loads(message)
		elif message and isinstance(message, dict):
			kwargs = message

		coinid = kwargs.get("coinid")
		if coinid and coinid.upper() not in self.types:
			self.error_403("Validate. Not valid coinid")
			return

		amount = kwargs.get("amount")
		if amount and not isinstance(amount, int):
			self.error_400("Validate. Not valid amount")
			return

	async def get_uid_by_address(self, *args, **kwargs):

		address = kwargs.get("address")
		coinid = kwargs.get("coinid")

		database = self.client[self.collection]
		collection = database[coinid]

		balance = await collection.find_one({"address": address})

		if not balance:
			return self.error_404("Not found current balance. ")

		return int(balance["uid"])


class Balance(Abstract):

	#@verify
	async def freeze(self, *args, **kwargs):
		"""
		Freeze users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		#super().validate(*args, **kwargs)
		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":uid})
		if not balance:
			return self.error_404(
				"Freeze. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Check if amount is enough
		difference = int(balance["amount_active"]) - int(amount) 
		if difference < 0:
			return self.error_403("Freeze. Insufficient amount in the account")
		# Decrement active amount and increment frozen amount
		await collection.find_one_and_update({"uid":uid},
						{"$inc":{"amount_active":-amount, "amount_frozen":amount}})
		
		# Return updated balance with excluded mongo _id field
		result = await collection.find_one({"uid":uid})

		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def unfreeze(self, *args, **kwargs):
		"""
		Unfreeze users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""
		super().validate(*args, **kwargs)

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":uid})
		if not balance:
			return self.error_404(
				"Unfreeze. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Check if amount is enough
		difference = balance["amount_frozen"] - amount 
		if difference < 0:
			return self.error_403("Unreeze. Insufficient frozen amount in the account")
		# Decrement active amount and increment frozen amount
		await collection.find_one_and_update({"uid":uid},{"$inc":{"amount_frozen":-amount}})
		await collection.find_one_and_update({"uid":uid},{"$inc":{"amount_active":amount}})
		# Return updated balance with excluded mongo _id field
		result = await collection.find_one({"uid":uid})
		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def add_active(self, *args, **kwargs):
		"""
		Increment users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""
		super().validate(*args, **kwargs)

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":int(uid)})
		if not balance:
			return self.error_404(
				"Add active. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Increment balance
		await collection.find_one_and_update({"uid":int(uid)},
							{"$inc":{"amount_active":amount}})
		# Return result with excluded mongo _id field
		result = await collection.find_one({"uid":int(uid)})
		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def add_frozen(self, *args, **kwargs):
		"""
		Increment frozen users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""
		super().validate(*args, **kwargs)

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		txid = kwargs.get("txid")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":uid})
		if not balance:
			return self.error_404(
				"Add frozen. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Increment balance
		await collection.find_one_and_update({"uid":uid},{"$inc":{"amount_frozen":amount}})
		# Set txid if exists
		if txid:
			await collection.find_one_and_update({"uid":uid},
										{"$set":{"txid":txid}})
		# Return result with excluded mongo _id field
		result = await collection.find_one({"uid":uid})
		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def sub_active(self, *args, **kwargs):
		"""
		Decrement active users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""
		super().validate()

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":uid})
		if not balance:
			return self.error_404(
				"Sub active. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Check if balance is enough
		difference = int(balance["amount_active"]) - int(amount)
		if difference < 0:
			return self.error_400("Sub active. Balance is not enough.")
		# Increment balance
		await collection.find_one_and_update({"uid":uid},{"$inc":{"amount_active":-amount}})
		# Return result with excluded mongo _id field
		result = await collection.find_one({"uid":uid})
		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def withdraw(self, *args, **kwargs):
		"""
		Decrement active users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""
		super().validate()

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":uid})
		if not balance:
			return self.error_404(
				"Sub active. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Check if balance is enough
		difference = int(balance["amount_active"]) - int(amount)
		if difference < 0:
			return self.error_400("Sub active. Balance is not enough.")
		# Increment balance
		await collection.find_one_and_update({"uid":uid},{"$inc":{"amount_active":-amount}})
		# Return result with excluded mongo _id field
		result = await collection.find_one({"uid":uid})
		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def sub_frozen(self, *args, **kwargs):
		"""
		Decrement frozen users balance

		Accepts:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount [integer] (amount for freezing)

		Returns:
			- uid [integer] (users id from main server)
			- coinid [string] (blockchain type in uppercase)
			- amount_active [integer] (activae users amount)
			- amount_frozen [integer] (frozen users amount)
		"""
		super().validate()

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get data from request
		uid = kwargs.get("uid")
		coinid = kwargs.get("coinid")
		amount = kwargs.get("amount")
		address = kwargs.get("address")

		try:
			amount = bson.int64.Int64(int(amount))
		except Exception as e:
			return {"error":403, "reason":str(e)}

		# Check if required fields exists
		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Connect to appropriate database
		database = self.client[self.collection]
		collection = database[coinid]
		# Check if balance exists
		balance = await collection.find_one({"uid":uid})
		if not balance:
			return self.error_404(
				"Sub frozen. Balance with uid:%s and type:%s not found." % (uid, coinid))
		# Check if balance is enough
		difference = int(balance["amount_frozen"]) - int(amount)
		if difference < 0:
			return self.error_400("Sub frozen. Balance is not enough.")
		# Increment balance
		await collection.find_one_and_update({"uid":uid},{"$inc":{"amount_frozen":-amount}})
		# Return result with excluded mongo _id field
		result = await collection.find_one({"uid":uid})
		return {i:result[i] for i in result if i != "_id"}

	#@verify
	async def get_active(self, *args, **kwargs):
		"""
		Get active users balance

		Accepts:
			- uid [integer] (users id)
			- types [list | string] (array with needed types or "all")

		Returns:
			{
				type [string] (blockchain type): amount
			}
		"""
		super().validate(*args, **kwargs)

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get daya from request
		coinids = kwargs.get("coinids")
		uid = kwargs.get("uid")
		address = kwargs.get("address")

		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		# Check if required fields exists
		if not all([coinids, uid]):
			return self.error_400("Get active. Missed required fields.")
		if isinstance(coinids, list):
			actives = {}
			for coinid in coinids:
				database = self.client[self.collection]
				collection = database[coinid]
				# Get current balance
				balance = await collection.find_one({"uid":uid})
				if not balance:
					return self.error_404(
						"Get active. Balance with uid:%s and type:%s not found" % (uid, coinid))
				# Collect actives
				actives[coinid] = balance["amount_active"]

		if isinstance(coinids, str):
			actives = {}
			for coinid in self.coinids:
				database = self.client[coinid]
				collection = database[self.collection]
				# Get current balance
				balance = await collection.find_one({"uid":uid})
				if not balance:
					return self.error_404(
						"Get active. Balance with uid:%s and type:%s not found" % (uid, coinid))
				# Collect actives
				actives[coinid] = balance["amount_active"]
		return actives

	#@verify
	async def get_frozen(self, *args, **kwargs):
		"""
		Get frozen users balance

		Accepts:
			- uid [integer] (users id)
			- types [list | string] (array with needed types or "all")

		Returns:
			{
				type [string] (blockchain type): amount
			}
		"""
		super().validate(*args, **kwargs)

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		# Get daya from request
		coinids = kwargs.get("coinids")
		uid = kwargs.get("uid")
		address = kwargs.get("address")
		# Check if required fields exists

		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		if not all([types, uid]):
			return self.error_400("Get frozen. Missed required fields.")
		if isinstance(types, list):
			actives = {}
			for coinid in coinids:
				database = self.client[self.collection]
				collection = database[coinid]
				# Get current balance
				balance = await collection.find_one({"uid":uid})
				if not balance:
					return self.error_404(
						"Get frozen. Balance with uid:%s and type:%s not found" % (uid, coinid))
				# Collect actives
				actives[coinid] = balance["amount_frozen"]

		if isinstance(coinids, str):
			actives = {}
			for coinid in self.types:
				database = self.client[coinid]
				collection = database[self.collection]
				# Get current balance
				balance = await collection.find_one({"uid":uid})
				if not balance:
					return self.error_404(
						"Get frozen. Balance with uid:%s and type:%s not found" % (uid, coinid))
				# Collect actives
				actives[coinid] = balance["amount_frozen"]
		return actives

	#@verify
	async def get_wallets(self, *args, **kwargs):
		"""
		Get users wallets by uid

		Accepts:
			- uid [integer] (users id)

		Returns a list:
			- [
					{
						"address": [string],
						"uid": [integer],
						"amount_active": [integer],
						"amount_frozen": [integer]
					},
				]
		"""
		super().validate(*args, **kwargs)

		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message"))

		uid = kwargs.get("uid")
		address = kwargs.get("address")

		if not uid and address:
			uid = await self.get_uid_by_address(address=address, coinid=coinid)
			if isinstance(uid, dict):
				return uid

		uid = int(uid)
		wallets = []
		for coinid in self.types:

			# Connect to appropriate database
			database = self.client[self.collection]
			collection = database[coinid]
			# Get wallets
			wallet = await collection.find_one({"uid":int(uid)})
			if not wallet:
				return self.error_404(
					f"Get wallets. Not found wallet with coinid {coinid} and uid {uid}")
			wallets.append({i:wallet[i] for i in wallet if i != "_id"})

		return {"wallets":wallets}


	#@verify 
	async def confirmbalance(self, *args, **kwargs):
		""" Confirm balance after trading

		Accepts:
		    - message (signed dictionary):
		        - "txid" - str
		        - "coinid" - str
		        - "amount" - int

		Returns:
		        - "address" - str
		        - "coinid" - str
		        - "amount" - int
		        - "uid" - int
		        - "unconfirmed" - int (0 by default)
		        - "deposit" - int (0 by default)

		Verified: True

		"""
		logging.debug("[+] -- Confirm balance debugging. ")
		# Get data from request
		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message", "{}"))

		txid = kwargs.get("txid")
		coinid = kwargs.get("coinid")
		buyer_address = kwargs.get("buyer_address")
		cid = kwargs.get("cid")
		address = kwargs.get("buyer_address")
		
		# Check if required fields exists
		if not all([coinid, cid, buyer_address, txid]):
		    return {"error":400, "reason": "Confirm balance. Missed required fields"}

		if not coinid in settings.bridges.keys():
			return self.error_400("Confirm balance. Invalid coinid: %s" % coinid)

		# Get offers price	
		self.account.blockchain.setendpoint(settings.bridges[coinid])
		offer = await self.account.blockchain.getoffer(cid=cid, 
											buyer_address=buyer_address)
		logging.debug("\n[+] -- Offer price")
		# Get offers price for updating balance
		amount = int(offer["price"])
		logging.debug(amount)

		coinid = "PUTTEST"
		# Get sellers account
		history_database = self.client[settings.HISTORY]
		history_collection = history_database[coinid]
		history = await history_collection.find_one({"txid":txid})

		account = await self.account.getaccountdata(public_key=history["public_key"])
		if not account:
			return self.error_404("Confirm balance. Not found current deal.")
		logging.debug("\n[+] -- Account")

		# Connect to balance database
		database = self.client[self.collection]
		balance_collection = database[coinid]

		# Try to update balance if exists
		updated = await balance_collection.find_one_and_update(
		                        {"uid":account["id"]}, 
		                        {"$inc":{"amount_active":int(amount)}})
		logging.debug("\n[+] -- Updated sellers account. ")
		logging.debug(updated)
		if not updated:
		    return {"error":404, 
		            "reason":"Confirm balance. Not found current transaction id"}

		# Decrement unconfirmed
		decremented = await balance_collection.find_one_and_update(
		                        {"uid":account["id"]}, 
		                        {"$inc":{"amount_frozen": -amount}})
		logging.debug("\n[+] -- Decremented account. ")
		logging.debug(decremented)

		if int(account["level"]) == 2:
		    await self.account.updatelevel(**{"id":account["id"], "level":3})

		return {i:updated[i] for i in updated if i != "_id" and i != "txid"}


	#@verify
	async def registerdeal(self, *args, **kwargs):
		"""
		"""
		# Get data from request
		if kwargs.get("message"):
			kwargs = json.loads(kwargs.get("message", "{}"))

		uid = int(kwargs.get("uid"))
		txid = kwargs.get("txid")
		coinid = kwargs.get("coinid")
		public_key = kwargs.get("public_key")
		cid = kwargs.get("cid")

		if not all([uid, txid, coinid]):
			return self.error_400("Register deal. Missed required fields.")

		# Database "Balance", collection "PUTTEST"
		database = self.client[settings.HISTORY]
		collection = database[coinid]

		# Save data to database
		await collection.insert_one({
					"uid": uid,
					"public_key": public_key,
					"cid": cid,
					"txid": txid,
					"unconfirmed": False
			})
		return {"result":"ok"}



balance = Balance()


@methods.add
async def freeze(*args, **kwargs):
	request = await balance.freeze(*args, **kwargs)
	return request

@methods.add
async def unfreeze(*args, **kwargs):
	request = await balance.unfreeze(*args, **kwargs)
	return request

@methods.add
async def add_active(*args, **kwargs):
	request = await balance.add_active(*args, **kwargs)
	return request

@methods.add
async def add_frozen(*args, **kwargs):
	request = await balance.add_frozen(*args, **kwargs)
	return request

@methods.add
async def sub_active(*args, **kwargs):
	request = await balance.sub_active(*args, **kwargs)
	return request

@methods.add
async def sub_frozen(*args, **kwargs):
	request = await balance.sub_frozen(*args, **kwargs)
	return request

@methods.add
async def get_active(*args, **kwargs):
	request = await balance.get_active(*args, **kwargs)
	return request

@methods.add
async def get_frozen(*args, **kwargs):
	request = await balance.get_frozen(*args, **kwargs)
	return request

@methods.add
async def get_wallets(*args, **kwargs):
	request = await balance.get_wallets(*args, **kwargs)
	return request

@methods.add
async def confirmbalance(*args, **kwargs):
	request = await balance.confirmbalance(*args, **kwargs)
	return request

@methods.add
async def registerdeal(*args, **kwargs):
	request = await balance.registerdeal(*args, **kwargs)
	return request



