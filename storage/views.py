# Builtins
import json
import logging

#Third-party
import tornado_components.web
from jsonrpcserver.aio import methods

import rpc_methods





class StorageHandler(tornado_components.web.ManagementSystemHandler):
	"""Class handler Storage API
	"""
	async def post(self):
		logging.debug("\n\n[+] -- Storage server debugging.")
		data = json.loads(self.request.body.decode())
		logging.debug(data)
		logging.debug("\n\n")
		response = await methods.dispatch(data)
		self.write(response)


	async def get(self):
		logging.debug("\n\n[+] -- Storage server debugging.")
		data = json.loads(self.request.body.decode())
		logging.debug(data)
		logging.debug("\n\n")
		response = await methods.dispatch(data) 
		self.write(response)



