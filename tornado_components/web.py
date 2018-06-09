import sys
import json
import time
import logging
import os
import datetime
from jsonrpcclient.tornado_client import TornadoClient
import tornado.web
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum
from bip32keys.bip32keys import Bip32Keys



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
			result = await super().request(method_name=kwargs["method_name"],
												message=message, signature=signature)
			return result
		except ConnectionRefusedError:
			return {"error":500, 
					"reason": "Service connection error."}
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
		if self.request.body:
			data = json.loads(self.request.body)
			message = data.get("message")
		elif self.request.arguments:
			data = {i:self.get_argument(i) for i in self.request.arguments}
			message = json.loads(data.get("message", "{}"))
		try:
			# Check if required fields exist
			assert "public_key" in data.keys(), "Missed public key in parameters"
			assert "message" in data.keys(), "Missed message in parameters"
			assert "signature" in data.keys(),"Missed signature in parameters"

			public_key = data["public_key"]
			signature = data["signature"]
			dumped_message = json.dumps(message).replace(" ", "")
			timestamp = data.get("timestamp", None)
			
			# Check if
			#assert ManagementSystemHandler.get_time_stamp() == timestamp, "Timestamps does not match. Try again."

		except Exception as e:
			self.set_status(403)
			self.write({"error":403, "reason": str(e)})
			raise tornado.web.Finish

		else:
			# Check if message and signature exist
			# If not - return 403 error code
			if not all([message, public_key, signature]):
				raise tornado.web.HTTPError(403)
			# If exist - call verifying static method
			
			try:
			    flag = Qtum.verify_message(dumped_message, signature, public_key)
			except Exception as e:
			    # If public key is not valid or it`s missing - return 404 error
			    self.set_status(403)
			    self.write({"error":403, 
			    			"reason":"Forbidden. Invalid signature." + str(e)})
			    raise tornado.web.Finish
			# If verifying is not valid - return 403 error
			if not flag:
			    self.status(403)
			    self.write({"error":403, 
			    			"reason":"Forbidden. Invalid signature."})


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

			    
