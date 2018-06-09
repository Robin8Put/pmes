from jsonrpcclient.http_client import HTTPClient 
from collections import OrderedDict
import json


class RobustTornadoClient(HTTPClient):
	"""Client processes refused connections and 
		sends email if happens the one.
	"""
	def request(self, *args, **kwargs):
		"""Overrided method. Returns jsonrpc response
		or fetches exception? returns appropriate data to client
		and response mail to administrator.
		"""
		try:
			#'{"jsonrpc": "2.0", "method": "ping", "id": 1}'
			#result = super().request(*args, **kwargs)
			message = json.dumps(kwargs)

			result = super().request(method_name=kwargs["method_name"],
												message=message)
			print(message)
			return result
		except ConnectionRefusedError:
			return {"error":500, 
					"reason": "Service connection error."}
		except Exception as e:
			return {"error":500, "reason": str(e)}



client = RobustTornadoClient("http://127.0.0.1:8004/api/balance")

r = client.request(method_name="incbalance", amount=20, uid=1)
print(r)
