import os
import sys
import json
import logging

from utils.tornado_components.web import SignedTornadoClient, RobustTornadoClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import settings
from pdms.qtum_bridge.robin8_billing import robin8_billing

with open(settings.qtum_settings_file) as qtum_settings:
	qtum = json.load(qtum_settings)
	
billing = robin8_billing.Robin8_Billig(qtum["billing"])

client_storage = SignedTornadoClient(settings.storageurl)
client_balance = SignedTornadoClient(settings.balanceurl)


async def upload_content_fee(*args, **kwargs):
	"""Estimating uploading content
	"""
	cus = kwargs.get("cus")
	owneraddr = kwargs.get("owneraddr")
	description = kwargs.get("description")
	coinid = kwargs.get("coinid", "PUT")

	#Check if required fields exists
	if not all([cus, owneraddr, description]):
		return {"error":400, "reason":"Missed required fields"}

	# Get upload content fee
	content_fee = billing.estimate_upload_fee(len(cus))
	descr_fee = billing.estimate_set_descr_fee(len(description))
	# Get users account
	user = await client_storage.request(method_name="getaccountbywallet", wallet=owneraddr)
	if "error" in user.keys():
		return user
	# Get users balance
	balances = await client_balance.request(method_name="getbalance", coinid=coinid, 
																	uid=user["id"])
	if isinstance(balances, dict):
		if "error" in balances.keys():
			return balance
	# Decrement users balance
	common_price = int(content_fee) + int(descr_fee)

	for w in balances:
		if coinid in w.values():
			balance = w
	diff = int(balance["amount"]) - common_price
	if diff < 0:
		return {"error":403, "reason": "Balance is not enough."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                        						coinid=coinid, amount=common_price)
	if "error" in decbalance.keys():
		return decbalance
	else:
		return {"result":"ok"}


async def update_description_fee(*args, **kwargs):
	"""
	"""
	cid = kwargs.get("cid")
	description = kwargs.get("description")
	owneraddr = kwargs.get("owneraddr")
	coinid = kwargs.get("coinid", "PUT")


	if not all([cid, description, owneraddr]):
		return {"error":400, "reason":"Missed required fields"}

	user = await client_storage.request(method_name="getaccountbywallet",
	    												wallet=owneraddr)
	if "error" in user.keys():
		return user

	balances = await client_balance.request(method_name="getbalance", uid=user["id"])

	if isinstance(balances, dict):
		if "error" in balances.keys():
			return balances
	
	for w in balances:
		if coinid in w.values():
			balance = w

	fee = billing.estimate_set_descr_fee(len(description))

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason":"Owner does not have enough balance."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	    													coinid=coinid, amount=fee)
	if "error" in decbalance.keys():
		return decbalance
	else:
		return {"result":"ok"}
		


async def change_owner_fee(*args, **kwargs):
	"""
	"""
	logging.debug("[+] -- Change owner fee. ")
	cid = kwargs.get("cid")
	new_owner = kwargs.get("new_owner")
	coinid = kwargs.get("coinid", "PUT")

	logging.debug(coinid)

	if not all([cid, new_owner]):
		return {"error":400, "reason":"Missed required fields"}

	user = await client_storage.request(method_name="getaccountdata",
	    				                            public_key=new_owner)
	if "error" in user.keys():
		return user

	balances = await client_balance.request(method_name="getbalance",
	                                uid=user["id"])
	
	if isinstance(balances, dict):
		if "error" in balances.keys():
			return balances

	for w in balances:
		if coinid in w.values():
			balance = w

	fee = billing.estimate_change_owner_fee()

	logging.debug(balance["amount"])

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason":"New owner does not have enough balance."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
										                   coinid=coinid, amount=fee)
	if "error" in decbalance.keys():
		return decbalance
	else:
		return {"result":"ok"}
		


async def sell_content_fee(*args, **kwargs):
	"""
	"""
	cid = kwargs.get("cid")
	new_owner = kwargs.get("new_owner")
	coinid = kwargs.get("coinid", "PUT")


	if not all([cid, new_owner]):
		return {"error":400, "reason":"Missed required fields"}

	user = await client_storage.request(method_name="getaccountdata",
	                        					public_key=new_owner)
	if "error" in user.keys():
		return user

	balances = await client_balance.request(method_name="getbalance", uid=user["id"])

	if isinstance(balances, dict):
		if "error" in balances.keys():
			return balances

	for w in balances:
		if coinid in w.values():
			balance = w

	fee = billing.estimate_sale_fee()

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason": "Balance is not enough."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                        						coinid=coinid, amount=fee)

	if "error" in decbalance.keys():
		return decbalance
	else:
		return {"result":"ok"}


async def set_price_fee(*args, **kwargs):
	"""
	"""
	cid = kwargs.get("cid")
	price = kwargs.get("price")
	owneraddr = kwargs.get("owneraddr")
	coinid = kwargs.get("coinid", "PUT")

	if not all([cid, price, owneraddr]):
		return {"error":400, "reason":"Missed required fields"}


	user = await client_storage.request(method_name="getaccountbywallet",
	                wallet=owneraddr)
	if "error" in user.keys():
		return user

	balances = await client_balance.request(method_name="getbalance", uid=user["id"])

	if isinstance(balances, dict):
		if "error" in balances.keys():
			return balances

	for w in balances:
		if coinid in w.values():
			balance = w

	fee = billing.estimate_set_price_fee()

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason": "Balance is not enough."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                									coinid=coinid, amount=fee)


	if "error" in decbalance.keys():
		return decbalance

	else:
		return {"result":"ok"}


async def set_make_offer_fee(*args, **kwargs):
	"""
	"""
	buyer_address = kwargs.get("buyer_address")
	coinid = kwargs.get("coinid", "PUT")

	user = await client_storage.request(method_name="getaccountbywallet",
	                wallet=buyer_address)
	if "error" in user.keys():
		return user

	balances = await client_balance.request(method_name="getbalance", uid=user["id"])

	if isinstance(balances, dict):
		if "error" in balances.keys():
			return balances

	for w in balances:
		if coinid in w.values():
			balance = w

	fee = billing.estimate_make_offer_fee()


	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason": "Balance is not enough."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                									coinid=coinid, amount=fee)
	print(decbalance)

	if "error" in decbalance.keys():
		return decbalance

	else:
		return {"result":"ok"}

































