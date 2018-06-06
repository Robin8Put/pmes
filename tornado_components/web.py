import sys
import json
import time
import logging
import datetime
from jsonrpcclient.tornado_client import TornadoClient
import tornado.web
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum



class RobustTornadoClient(TornadoClient):
	"""Client processes refused connections and 
		sends email if happens the one.
	"""
	async def request(self, *args, **kwargs):
		"""Overrided method. Returns jsonrpc response
		or fetches exception? returns appropriate data to client
		and response mail to administrator.
		"""
		try:
			result = await super().request(*args, **kwargs)
			return result
		except ConnectionRefusedError:
			return {"error":500, 
					"reason": "Service connection error."}
		except Exception as e:
			return {"error":500, "reason": str(e)}


	
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
		data = json.loads(self.request.body)
		try:
			# Check if required fields exist
			assert "public_key" in data.keys(), "Missed public key in parameters"
			assert "message" in data.keys(), "Missed message in parameters"
			assert "signature" in data.keys(),"Missed signature in parameters"

			public_key = data["public_key"]
			message = data["message"]
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
			    			"reason":"Forbidden. Invalid signature.---"})


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

			    
