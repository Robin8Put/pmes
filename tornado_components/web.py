import json
import time
import logging
import datetime
from jsonrpcclient.http_client import HTTPClient
import tornado.web
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum



	

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
		data = {k:self.get_argument(k) for k in self.request.arguments}
		logging.debug(data)

		try:
			public_key = data["public_key"]
			message = data["message"]
			signature = data["signature"]

			dumped_message = json.loads(message)
			timestamp = dumped_message.get("timestamp", None)
			
			assert ManagementSystemHandler.get_time_stamp() == timestamp

		except:
			self.set_status(403)
			self.write("Missed required fields or timestamps do not match")
			raise tornado.web.Finish

		else:
			# Check if message and signature exist
			# If not - return 403 error code
			if not all([message, public_key, signature]):
				raise tornado.web.HTTPError(403)
			# If exist - call verifying static method
			
			try:
			    flag = Qtum.verify_message(message, signature, public_key)
			except:
			    # If public key is not valid or it`s missing - return 404 error
			    raise tornado.web.HTTPError(403)
			# If verifying is not valid - return 403 error
			if not flag:
			    raise tornado.web.HTTPError(403)

	def get(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

	def post(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

	def put(self, *args, **kwargs):
		self.set_status(405)
		self.write({"error":405, "reason":"Method not allowed."})

			    
