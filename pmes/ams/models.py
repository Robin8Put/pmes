import requests
from tornado_components.rpc_client import RPCClient
import settings
import logging



model = {
	"unique": "public_key",
	"required": ("public_key", "email", "device_id"),
	"default": {"count":1, "level":2},
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

	# check unique constraints
	unique = {model["unique"]:data[model["unique"]]}
	request = requests.get(host, params=unique)

	try:
		_id = request["id"]
	except:
		# Reload data.
		row = {i:data[i] for i in data 
				if i in model["required"] or i in model["optional"]}
		row.update({i:model["default"][i] for i in model["default"]})
		#response = RPCClient.post(host, "createaccount", row)
		response = requests.post(host, data=row)

		return response.json()
	else:
		return {"error": 400, 
				"reason":"Account with current field does exist"}
