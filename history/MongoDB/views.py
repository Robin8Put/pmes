
import json
import logging

from jsonrpcserver.aio import methods
from jsonrpcserver import dispatch
import tornado.web

import models

# Create database cursor instance
history = models.MongoStorage()

def log(**data):
	"""RPC method for logging events
	Makes entry with new account creating
	Return None
	"""
	# Get data from request body
	entry = {
		"module": data["params"]["module"],
		"event": data["params"]["event"],
		"timestamp": data["params"]["timestamp"],
		"arguments": data["params"]["arguments"]
	}
	# Call create metod for writing data to database
	history.create(entry)



class HistoryHandler(tornado.web.RequestHandler):
	"""Handler of RPC requests
	Accepts jsorpc data
	"""
	SUPPORTED_METHODS = ['GET','POST']

	def post(self):
		"""Accepts jsorpc post request.
		Retrieves data from request body.
		Calls log method for writung data to database
		"""
		data = json.loads(self.request.body.decode())
		response = dispatch([log],{'jsonrpc': '2.0', 
					'method': 'log', 'params': data, 'id': 1})

					


