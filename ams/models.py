import requests
from tornado_components.rpc_client import RPCClient
from jsonrpcclient.http_client import HTTPClient
import settings
import logging
import json



model = {
	"unique": ["email", "public_key"],
	"required": ("public_key", "email", "device_id"),
	"default": {"count":1, "level":2, "news_count":0},
	"optional": ("phone",)
}

def create(host, data):
	"""Describes, validates data.
	Calls create account method.
	"""
	if not isinstance(data, dict):
			return {"error": 400,
					"reason": "Issue with creating ('post' function)"}

	# check if all required
	required = all([True if i in data.keys() else False 
							for i in model["required"]])
	if not required:
		return {"error": 400,
				"reason":"Missed required fields"}

	client = HTTPClient(host)

	# Unique constraint
	get_account = client.request(method_name="getaccountdata",
								public_key=data["public_key"])
	# Try get account with current public key
	

	try:
		# If does exist - return unique error
		error_code = get_account["error"]
	except KeyError:
		return {"error": 400,
				"reason": "Unique violation error"}
	else:
		# Reload data.
		row = {i:data[i] for i in data 
				if i in model["required"] or i in model["optional"]}
		row.update({i:model["default"][i] for i in model["default"]})
		logging.debug("[+] -- Data for inserting")
		#response = RPCClient.post(host, "createaccount", row)
		response = client.request(method_name="createaccount", **row)
		return response

