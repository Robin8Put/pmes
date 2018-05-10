# Builtins
import json
import time
import logging
import datetime
import string
from random import choice
from hashlib import sha256

#Third-party
from jsonrpcserver import dispatch
import tornado.web
import tornado_components.web 
import tornado_components.mongo
from jsonrpcserver.aio import methods
import requests

# Locals
import settings
import tornado_components.mongo
from . import rpc_methods
from tornado_components.rpc_client import RPCClient
from qtum_utils.qtum import Qtum


table = tornado_components.mongo.Table(dbname=settings.DBNAME,
										collection=settings.COLLECTION)


class StorageHandler(tornado_components.web.ManagementSystemHandler):
	"""Class handler Storage API
	"""
	def post(self):
		"""Create new account
		"""
		# Get data from request body
		data = { k: self.get_argument(k) for k in self.request.arguments}
		# Connect to database
		table = tornado_components.mongo.Table(dbname=settings.DBNAME,
										collection=settings.COLLECTION)
		# Get just created document
		document = table.insert(**data)
		# Return just created document data
		self.write({i:document[i] for i in document if i != "_id"})

	def get(self):
		"""Retrieve data from database
		"""
		data = {k: self.get_argument(k) for k in self.request.arguments}
		
		public_key = data.get("public_key", None)

		if not public_key:
			self.write({"error":403, "reason":"Forbidden"})

		response = table.find(public_key=public_key)

		self.write({i:response[i] for i in response if i != "_id"})

			

