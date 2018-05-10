# Builtins
import json
import logging

# Third-party
import pymongo


class MongoStorage(object):
	"""Custom driver for writing data to mongodb
	By default database name is 'profile_management_system',
		collection name is 'history'
	"""

	def __init__(self, db_name=None, collection=None):
		# Set database parameters
		if not db_name:
			self.db_name = "profile_management_system"
		else:
			self.db_name = db_name
		if not collection:
			self.collection = "history"
		else:
			self.collection = collection

		self.client = pymongo.MongoClient()

		self.database = self.client[self.db_name]

		# Set collection nsme
		self.history = self.database[self.collection]


	def create(self, data):
		"""Creates new entry in mongo database
		"""		
		q = self.history.insert_one(data).inserted_id
		logging.debug(self.history.find_one({"_id":q}))




