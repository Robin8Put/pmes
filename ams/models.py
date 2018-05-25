import requests
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

def create_account(host, data):
	"""Describes, validates data.
	Calls create account method.
	"""
	message = json.loads(data.get("message", "{}"))
	data = {**data, **message}
	# check if all required
	required = all([True if i in data.keys() else False for i in model["required"]])

	if not required:
		return {"error": 400,
				"reason":"Missed required fields"}

	# Unique constraint
	client = HTTPClient(host)
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
		response = client.request(method_name="createaccount", **row)

		return response


def create_wallet(host, data):
	"""Creates wallet table with account relation
	"""
	client = HTTPClient(host)
	response = client.request(method_name="createwallet", **data)
	return response


