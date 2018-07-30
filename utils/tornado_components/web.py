import sys
import json
import time
import logging
import os
import re
import datetime
from jsonrpcclient.http_client import HTTPClient
from jsonrpcclient.tornado_client import TornadoClient
import tornado.web
from utils.tornado_components.timestamp import get_time_stamp
from utils.qtum_utils.qtum import Qtum
from utils.bip32keys.bip32keys import Bip32Keys
import settings




class SignedHTTPClient(HTTPClient):
	"""Client processes refused connections and 
		sends email if happens the one.
	"""
	def request(self, *args, **kwargs):
		"""Overrided method. Returns jsonrpc response
		or fetches exception? returns appropriate data to client
		and response mail to administrator.
		"""
		try:
			import settings

			with open(os.path.join(settings.BASE_DIR, "keys.json")) as f:
				keys = json.load(f)
				privkey = keys["privkey"]

			message = json.dumps(kwargs)
			signature = Bip32Keys.sign_message(message, privkey)
			result = super().request(method_name=kwargs["method_name"],
												message=message, signature=signature)
			return result
		except ConnectionRefusedError:
			return {"error":500, 
					"reason": "Service connection error."}
		except Exception as e:
			return {"error":500, "reason": str(e)}



class SignedTornadoClient(TornadoClient):
	"""Client processes refused connections and 
		sends email if happens the one.
	"""
	async def request(self, *args, **kwargs):
		"""Overrided method. Returns jsonrpc response
		or fetches exception? returns appropriate data to client
		and response mail to administrator.
		"""
		try:
			import settings

			with open(os.path.join(settings.BASE_DIR, "keys.json")) as f:
				keys = json.load(f)
				privkey = keys["privkey"]

			message = json.dumps(kwargs)
			signature = Bip32Keys.sign_message(message, privkey)

			Bip32Keys.verify_message(message, signature, keys["pubkey"])
			result = await super().request(method_name=kwargs["method_name"],
												message=message, signature=signature)
			return result
		#except ConnectionRefusedError:
		#	return {"error":500, 
		#			"reason": "Service connection error."}
		except Exception as e:
			return {"error":500, "reason": str(e)}


class RobustTornadoClient(TornadoClient):
	async def request(self, *args, **kwargs):
		try:
			result = await super().request(*args, **kwargs)
		except ConnectionRefusedError:
			result = {"error":500, "reason":"Service connection error"}
		return result



class ManagementSystemHandler(tornado.web.RequestHandler):
	"""Overloaded class.
	Contains:
		- sign-verify decorators for both http and rpc requests
	"""

	@staticmethod
	def get_time_stamp():
		ts = time.time()
		return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')


	def verify(self):
		"""Abstract method.
		Signature verifying logic.

		"""
		logging.debug("\n\n")
		logging.debug("[+] -- Verify debugging")
		logging.debug("\n\n")

		if self.request.body:
			logging.debug("\n Request body")
			logging.debug(self.request.body)
			data = json.loads(self.request.body)
			message = json.dumps(data.get("message")).replace(" ", "")
			logging.debug("\n")
			logging.debug(message)

		elif self.request.arguments:
			logging.debug("\n Arguments")
			logging.debug(self.request.arguments)
			data = {i:self.get_argument(i) for i in self.request.arguments}
			message = data.get("message", "{}")
			logging.debug(message)

		try:
			# Check if required fields exist
			assert "public_key" in data.keys(), "Missed public key in parameters"
			assert "message" in data.keys(), "Missed message in parameters"
			assert "signature" in data.keys(),"Missed signature in parameters"
			public_key = data["public_key"]
			signature = data["signature"]
			timestamp = data.get("timestamp", None)
			
			# Check if
			#assert ManagementSystemHandler.get_time_stamp() == timestamp, "Timestamps does not match. Try again."

		except Exception as e:
			self.set_status(403)
			self.write({"error":403, "reason": "Missing signature " + str(e)})
			raise tornado.web.Finish

		else:
			# Check if message and signature exist
			# If not - return 403 error code
			if not all([message, public_key, signature]):
				raise tornado.web.HTTPError(403)
		# If exist - call verifying static method
		try:
			logging.debug("\n[] Try block. Verifying")
			logging.debug(message)
			logging.debug(signature)
			logging.debug(public_key)
			flag = Qtum.verify_message(message, signature, public_key)
		except Exception as e:
			# If public key is not valid or it`s missing - return 404 error
			#self.set_status(403)
			#self.write({"error":403, 
			#			"reason":"Forbidden. Invalid signature." + str(e)})
			#raise tornado.web.Finish
			logging.debug("\n Exception")
			logging.debug(str(e))
			pass


	def get(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

	def post(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

	def put(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

	def delete(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

	def options(self):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

			    
