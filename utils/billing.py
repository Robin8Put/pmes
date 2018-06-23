import os
import sys

from tornado_components.web import SignedTornadoClient, RobustTornadoClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import settings
from pdms.qtum_bridge.robin8_billing import robin8_billing


billing = robin8_billing.Robin8_Billig(settings.BILLING_FILE)

client_storage = RobustTornadoClient(settings.storageurl)
client_balance = SignedTornadoClient(settings.balanceurl)


async def upload_content_fee(*args, **kwargs):
	"""Estimating uploading content
	"""
	cus = kwargs.get("cus")
	owneraddr = kwargs.get("owneraddr")
	description = kwargs.get("description")
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
	balance = await client_balance.request(method_name="getbalance", uid=user["id"])
	if "error" in balance.keys():
		return balance
	# Decrement users balance
	common_price = int(content_fee) + int(descr_fee)
	diff = int(balance["amount"]) - common_price
	if diff < 0:
		return {"error":403, "reason": "Balance is not enough."}
	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                        amount=common_price)
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

	if not all([cid, description, owneraddr]):
		return {"error":400, "reason":"Missed required fields"}

	user = await client_storage.request(method_name="getaccountbywallet",
	    												wallet=owneraddr)
	if "error" in user.keys():
		return user

	balance = await client_balance.request(method_name="getbalance", uid=user["id"])
	if "error" in balance.keys():
		return balance

	fee = billing.estimate_set_descr_fee(len(description))

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason":"Owner does not have enough balance."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	    																amount=fee)
	if "error" in decbalance.keys():
		return decbalance
	else:
		return True


async def change_owner_fee(*args, **kwargs):
	"""
	"""
	cid = kwargs.get("cid")
	new_owner = kwargs.get("new_owner")

	if not all([cid, new_owner]):
		return {"error":400, "reason":"Missed required fields"}

	user = await client_storage.request(method_name="getaccountdata",
	    				                            public_key=new_owner)
	if "error" in user.keys():
		return user

	balance = await client_balance.request(method_name="getbalance",
	                                uid=user["id"])
	if "error" in balance.keys():
		return balance

	fee = billing.estimate_change_owner_fee()

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason":"New owner does not have enough balance."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
										                    amount=fee)
	if "error" in decbalance.keys():
		return decbalance
	else:
		return True


async def sell_content_fee(*args, **kwargs):
	"""
	"""
	cid = kwargs.get("cid")
	buyer_pubkey = kwargs.get("buyer_pubkey")

	if not all([cid, buyer_address]):
		return {"error":400, "reason":"Missed required fields"}

	user = await client_storage.request(method_name="getaccountdata",
	                        					public_key=buyer_pubkey)
	if "error" in user.keys():
		return user

	balance = await client_balance.request(method_name="getbalance", uid=user["id"])

	if "error" in balance.keys():
		return balance

	fee = billing.estimate_sale_fee()

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason": "Balance is not enough."}

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                        amount=fee)

	if "error" in decbalance.keys():
		return decbalance
	else:
		return True


async def set_price_fee(*args, **kwargs):
	"""
	"""
	cid = kwargs.get("cid")
	price = kwargs.get("price")
	owneraddr = kwargs.get("owneraddr")

	if not all([cid, price, owneraddr]):
		return {"error":400, "reason":"Missed required fields"}

	fee = billing.estimate_set_price_fee()

	user = await client_storage.request(method_name="getaccountbywallet",
	                wallet=owneraddr)
	if "error" in user.keys():
		return user

	balance = await client_balance.request(method_name="getbalance", uid=user["id"])

	if "error" in balance.keys():
		return balance

	decbalance = await client_balance.request(method_name="decbalance", uid=user["id"],
	                amount=fee)

	if "error" in decbalance.keys():
		return decbalance

	if int(balance["amount"]) - int(fee) < 0:
		return {"error":403, "reason": "Balance is not enough."}
	else:
		return True

































