import json
import time
import datetime
import logging

from jsonrpcclient.http_client import HTTPClient
import requests
import tornado.web

from qtum_utils.qtum import Qtum


class RPCClient(object):
	"""Custom jsonrpc client
	Include processing of connection errors
	"""

	@classmethod
	def request(cls, host, method):

		# Create new client for rpc request
		client = HTTPClient(host)

		# Connection errors processing
		
		response = client.request(method_name=method)
		return response


	@classmethod
	def post(cls, host, method, kwargs):

		# Create new client for rpc request
		client = HTTPClient(host)
		body='{"jsonrpc":"2.0","method":"%s","params":%s, "id":1}' % (
									method,json.dumps(kwargs))

		response = client.send(body)
		return response


	@staticmethod
	def lastblockid(host):
		"""Return last block id
		"""
		response = RPCClient.request(host,"lastblockid")
		if response:
			return {"lastblockid": response}
		else:
			return {"error": 404, "reason": "Not found"}


	@staticmethod
	def data_from_blockchain(host, data):
		"""Accepts:
		- cid
		- hash
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}


		cid = data.get("cid", None)
		hash_ = data.get("hash", None)

		if cid and isinstance(cid, int):
			owner = RPCClient.post(host,"ownerbycid",{"cid":cid})
			data = RPCClient.post(host,"readbycid",{"cid":cid})
			response = {"owner":owner, "data":data}
			if response:
				return response
			else:
				return {"error":404,"reason":"Not found"}
		elif hash_:
			cid = RPCClient.post(host,"getcid",{"hash":hash_})
			data = RPCClient.post(host,"ipfscat",{"hash":hash_})
			owner = RPCClient.post(host,"ownerbycid",{"cid":cid})
			response = {"cid":cid,"data":data,"owner":owner}
			if response:
				return response
			else:
				return {"error":404,"reason":"Not found"}
		elif not cid and not hash_:
			return {"error": 400,
					"reason":"Missed required fields"}

		return {"error":404,"reason":"Not found"}

	


	@staticmethod
	def getownerbycid(host, data):
		"""Accepts
		- cid
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		cid = data.get("cid", None)
		if cid:
			data = {"cid":cid}
			response = RPCClient.post(host,"ownerbycid",data)
			if response:
				return response
			else:
				return {"error":404,"reason":"Not found"}
		else:
			return {"error":400,
					"reason":"Missed cid or the one is not digit."}

		


	@staticmethod
	def getcontentdescr(host, data):
		"""Accepts
		- cid
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		cid = data.get("cid", None)
		if cid:
			data = {"cid":cid}
			response = RPCClient.post(host,"descrbycid",data)
			if response:
				return response
			else:
				return {"error":404,"reason":"Not found"}
		else:
			return {"error": 400,
					"reason":"Missed cid or the one is not digit."}

		


	@staticmethod
	def postcontent(host, data):
		"""Writes content to blockchain
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		public_key = data.get("public_key", None)
		cus = data.get("cus", None)

		if all([public_key, cus]):
			owneraddr = Qtum.public_key_to_hex_address(public_key)
			data = {"cus":cus, "owneraddr":owneraddr}
			response = RPCClient.post(host,"makecid",data)
			if response:
				return response
			else:
				return {"error":404,"reason":"Not found"}
		else:
			return {"error": 400,
					"reason":"Missed required fields"}



	@staticmethod
	def setdescrforcid(host, data):
		"""Accepts
		- cid
		- description
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		cid = data.get("cid", None)
		descr = data.get("descr", None)

		if all([cid, descr]):
			data = {"cid":cid, "descr":descr}
			response = RPCClient.post(host,"setdescrforcid",data)
			if response:
				return response
			else:
				return {"error":404, "reason":"Not found"}
		else:
			return {"error":400,
					"reason":"Missed required fields or cid is not digit."}
		


	@staticmethod
	def last_access_string(host, data):
		"""Accepts 
		- cid
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		cid = data.get("cid", None)
		if cid:
			response = RPCClient.post(host,"last_access_string",{"cid":cid})
			if response:
				return response
			else:
				return {"error":404, "reason":"Not found"}
		else:
			return {"error":400,
					"reason":"Missed required parameters or cid is not digit."}


	@staticmethod
	def changeowner(host, data):
		"""Accepts:
		- cid
		- public_key
		- new_owner public key
		- access string
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		cid = data.get("cid", None)
		public_key = data.get("public_key", None)
		new_owner = data.get("new_owner", None)
		access_string = data.get("access_string", None)

		if all([cid, public_key, new_owner, access_string]):
			owneraddr = RPCClient.getownerbycid(host,{"cid":cid})
			if Qtum.public_key_to_hex_address(public_key) == owneraddr:
				data = {"cid":cid,
						"new_owner":Qtum.public_key_to_hex_address(new_owner),
						"access_string":access_string}
				response = RPCClient.post(host,"changeowner",data)
				if response:
					return response
				else:
					return {"error":404, "reason":"Not found"}
			else:
				return {"error":404, 
						"reason":"Owner address does not match."}
		else:
			return {"error":400,
					"reason":"Missed required parameters."}



	@staticmethod
	def sellcontent(host, data):
		"""Accepts:
		- cid
		- public_key
		- buyer_pubkey
		- access_string
		"""
		if not isinstance(data, dict):
			return {"error": 400,
					"reason":"Attribute type must be dict"}

		cid = data.get("cid", None)
		public_key = data.get("public_key", None)
		buyer_pubkey = data.get("buyer_pubkey", None)
		access_string = data.get("access_string", None)

		if all([cid, public_key, buyer_pubkey, access_string]):
			owneraddr = RPCClient.getownerbycid(host,{"cid":cid})
			pk = Qtum.public_key_to_hex_address(public_key)
			if pk == owneraddr:
				data = {"cid":cid,
					"buyer_addr":Qtum.public_key_to_hex_address(buyer_pubkey),
					"access_string":access_string}
				response = RPCClient.post(host,"sellcontent",data)
				if response:
					return response
				else:
					return {"error":404, "reason":"Not found"}
			else:
				return {"error":404, 
						"reason":"Owner address does not match."}
		else:
			return {"error":400,
					"reason":"Missed required parameters."}






