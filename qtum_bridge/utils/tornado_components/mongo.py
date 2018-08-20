import json
import logging

import pymongo
from motor.motor_tornado import MotorClient

class Table(object):
	"""Custom driver for writing data to mongodb
	By default database name is 'profile_management_system',
		collection name is 'history'
	"""

	def __init__(self, dbname, collection):
		# Set database parameters

		self.client = MotorClient()

		self.database = self.client[dbname]

		self.collection = self.database[collection] 


	async def autoincrement(self):
		collection = self.database.autoincrement
		counter = await collection.find_one({"name":"counter"})
		if not counter:
			await collection.insert_one({"name":"counter", "id": 0})
		await collection.find_one_and_update(
							{"name": "counter"},
							{"$inc": {"id": 1}})
		counter = await collection.find_one({"name":"counter"})
		return counter["id"]



	async def read(self, *_id):
		"""Read data from database table.
		Accepts ids of entries.
		Returns list of results if success
			or string with error code and explanation.

		read(*id) => [(result), (result)] (if success)
		read(*id) => [] (if missed)
		read() => {"error":400, "reason":"Missed required fields"}
		"""
		if not _id:
			return {"error":400, 
					"reason":"Missed required fields"}

		result = []
		for i in _id:
			document = await self.collection.find_one({"id":i})
			try:
				result.append({i:document[i] for i in document
												if i != "_id"})
			except:
				continue
		return result



	async def insert(self, **kwargs):
		"""
		Accepts request object, retrieves data from the one`s body
		and creates new account. 
		"""
		
		if kwargs:
			# Create autoincrement for account
			pk = await self.autoincrement()
			kwargs.update({"id": pk})

			# Create account with received data and autoincrement
			await self.collection.insert_one(kwargs)

			row = await self.collection.find_one({"id": pk})

		else:
			row = None

		if row:
			return {i:row[i] for i in row if i != "_id"}
		else:
			return {"error":500, 
					"reason":"Not created"}



	async def find(self, **kwargs):
		"""Find all entries with given search key.
		Accepts named parameter key and arbitrary values.
		Returns list of entry id`s.

		find(**kwargs) => document (if exist)
		find(**kwargs) => {"error":404,"reason":"Not found"} (if does not exist)
		find() => {"error":400, "reason":"Missed required fields"}
		"""
		if not isinstance(kwargs, dict) and len(kwargs) != 1:
			return {"error":400, 
					"reason":"Bad request"}
		document = await self.collection.find_one(kwargs)
		if document:
			return document
		else:
			return {"error":404, "reason":"Not found"}




	async def update(self, _id=None, **new_data):
		"""Updates fields values.
		Accepts id of sigle entry and 
			fields with values.

		update(id, **kwargs) => {"success":200, "reason":"Updated"} (if success)
		update(id, **kwargs) => {"error":400, "reason":"Missed required fields"} (if error)
		"""
		if not _id or not new_data:
			return {"error":400, 
					"reason":"Missed required fields"}

		document = await self.collection.find_one({"id":_id})
		if not document:
			return {"error":404, 
					"reason":"Not found"}

		for key in new_data:
			await self.collection.find_one_and_update(
							{"id": _id},
							{"$set": {key: new_data[key]}}
						)
		updated = await self.collection.find_one({"id":_id})
		return {"success":200, "reason": "Updated", **updated}


	async def delete(self, _id=None):
		"""Delete entry from database table.
		Accepts id.
		delete(id) => 1 (if exists)
		delete(id) => {"error":404, "reason":"Not found"} (if does not exist)
		delete() => {"error":400, "reason":"Missed required fields"}
		"""
		if not _id:
			return {"error":400, 
					"reason":"Missed required fields"}

		document = await self.collection.find_one({"id": _id})

		if not document:
			return {"error":404, 
					"reason":"Not found"}

		deleted_count = await self.collection.delete_one(
							{"id": _id}).deleted_count

		return deleted_count
















