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
	async def post(self):
		"""Create new account
		"""
		# Get data from request body
		data = json.loads(self.request.body.decode())
		# Get just created document
		document = await methods.dispatch(data)
		# Return just created document data
		self.write(document)



	async def get(self):
		"""Retrieve data from database
		"""
		# Get data from request body
		data = json.loads(self.request.body.decode())
		if not data.get("public_key", None):
			self.write({"error":403, "reason":"Forbidden"})
		response = await methods.dispatch(data) 
		self.write(response)



