# Builtins
import json
import logging

#Third-party
import tornado_components.web 
from jsonrpcserver.aio import methods

# Locals
from . import rpc_methods




class StorageHandler(tornado_components.web.ManagementSystemHandler):
	"""Class handler Storage API
	"""
	async def post(self):
		data = json.loads(self.request.body.decode())
		response = await methods.dispatch(data)
		self.write(response)


	async def get(self):
		data = json.loads(self.request.body.decode())
		response = await methods.dispatch(data) 
		self.write(response)



