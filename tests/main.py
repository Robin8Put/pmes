import json
import time
import datetime
import sys
import os
import string
import random

import requests
import pymongo

from tornado_components import mongo
from jsonrpcclient.http_client import HTTPClient
from bip32keys.bip32keys import Bip32Keys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings
from qtum_utils.qtum import Qtum



def get_time_stamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

###############################################################################
							# Create account with valid data
def create_account_with_valid_data():
	print("---------------------------------------------------------------------")
	print("\n[+] -- Creating seller")
	#time.sleep(1)
	url = "%s:%s%s" % (settings.host, settings.pmesport, settings.ENDPOINTS["ams"])
	print("Request to:   " + url)
	#time.sleep(2)
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	email = "heroyooki@gmail.com"
	device_id = "lenovo"
	message = json.dumps({
			"email": email,
			"device_id": device_id,
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	request = requests.post(url, data=data)
	print(request.text)
	print("-------------------------------------------------------------------")

#################################################################################
							# Get account data
def getaccountdata():
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	print("---------------------------------------------------------------------")
	print("\n[+] -- Receiving account data")
	time.sleep(1)
	url = "%s:%s%s%s" % (settings.host, settings.pmesport, 
						settings.ENDPOINTS["ams"], public_key)
	print("Request to:   " + url)
	time.sleep(2)
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	message = json.dumps({
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key),
	}
	request = requests.get(url, params=data)
	print(request.text)


#################################################################################
							# Create account with existing data
def create_account_with_existing_data():
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	email = "denis@mail.ru"
	device_id = "lenovo"
	message = json.dumps({
			"email": email,
			"device_id": device_id,
			"timestamp": get_time_stamp()
		})
	data1 = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key),
		"email":email,
		"device_id":device_id
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, settings.ENDPOINTS["ams"])
	request = requests.post(url, data=data1)
	assert "error" in request.json().keys()
	assert request.json()["error"] == 400			

##################################################################################
							# Create account with invalid data (wrong message)
def create_account_with_invalid_data1():
	public_key = "040b2a27e6a40145d572392f01c3e9d5dd39ac3514636ae07382d928e803ec708a8c79cfdbde03b9f9c4bb7a982a9bb13f796576ba2b40384a34389908b8a0e2b1"
	private_key = "4361a55a6120e4d82c44cfd9415a70a9708eda256192092f0f7517820df2e56b"
	email = "artem@mail.ru"
	device_id = "hp"
	message = json.dumps({
		"email": email,
		"device_id": device_id,
		"timestamp": get_time_stamp()
	})
	data1 = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message + "error", private_key),
		"email":email,
		"device_id":device_id
		}
	url = "%s:%s%s" % (settings.host, settings.pmesport, settings.ENDPOINTS["ams"])
	request = requests.post(url, data=data1)
	assert request.status_code == 403


#################################################################################
						# Create account with invalid data (wrong public key)
def create_account_with_invalid_data2():
	public_key = "040b2a27e6a40145d572392f01c3e9d5dd39qw3514636ae07382d928e803ec708a8c79cfdbde03b9f9c4bb7a982a9bb13f796576ba2b40384a34389908b8a0e2b1"
	private_key = "4361a55a6120e4d82c44cfd9415a70a9708eda256192092f0f7517820df2e56b"
	email = "artem@mail.ru"
	device_id = "hp"
	message = json.dumps({
			"email": email,
			"device_id": device_id,
			"timestamp": get_time_stamp()
		})
	data1 = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message + "error", private_key),
		"email":email,
		"device_id":device_id
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, settings.ENDPOINTS["ams"])
	request = requests.post(url, data=data1)
	assert request.status_code == 403


##################################################################################
						# Write data to blockchain
def write_data_to_blockchain():
	print("\n[+] -- Writing data to blockchain")
	time.sleep(1)
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/content" % public_key)
	print("Request to:   " + url)
	time.sleep(2)
	message = json.dumps({
			"cus": id_generator(),
			"description":id_generator(),
			"price": 3,
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	request = requests.post(url, data=data)
	print(request.text)
	print("--------------------------------------------------------------------")



#################################################################################
						# Write invalid data to blockchain (missed cus)
def write_invalid_data_to_blockchain():
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/content" % public_key)
	message = json.dumps({
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	request = requests.post(url, data=data)
	assert request.status_code == 400
	assert request.json()["reason"] == "Missed required fields"

##################################################################################
						# Get data from blockchain
def get_data_from_blockchain(hash_):
	print("\n[+] -- Receiving data from blockchain")
	time.sleep(1)
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/content" % public_key)
	print("Request to:  " + url)
	time.sleep(2)

	data = {
		"hash": hash_
	}
	request = requests.get(url, params=data)
	print(request.text)
	print("----------------------------------------------------------------------")

##################################################################################
						# Set price for content
def setprice_for_content(cid, price):
	print("\n[+] -- Setting price for content")
	time.sleep(1)
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/price" % cid)
	print("Request to:   " + url)
	time.sleep(2)
	message = json.dumps({
			"cid":cid,
			"price":price,
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	request = requests.post(url, data=data)
	print(request.text)
	response = requests.get(url)
	print("----------------------------------------------------------------------")

#################################################################################
						# Set description for content




##################################################################################
						# Create buyer account
def create_buyer_with_valid_data():
	print("\n[+] -- Creating buyers account")
	time.sleep(1)
	public_key = "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"
	private_key = "1ebaa1c3b723a04cfbcdc39bebaebac23da71b5f4f95607d0793958b993d758f"
	email = "heroyooki@gmail.com"
	device_id = "lenovo"
	message = json.dumps({
			"email": email,
			"device_id": device_id,
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key),
		"email":email,
		"device_id":device_id
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, settings.ENDPOINTS["ams"])
	print("Request to " + url)
	time.sleep(2)
	request = requests.post(url, data=data)
	print(request.text)
	assert "public_key" in request.json().keys() 
	assert "balance" in request.json().keys()
	assert request.json()["balance"] >= 0
	assert request.json()["email"] == "heroyooki@gmail.com"
	print("\nBuyers id is: " + str(request.json()["id"]))
	print("----------------------------------------------------------------------")


##################################################################################
						# Increment buyers balance
def increment_buyers_balance(amount, uid):
	print("\n[+] -- Refilling buyers balance")
	time.sleep(1)
	client = HTTPClient(settings.balanceurl)
	client.request(method_name="incbalance", uid=uid, amount=amount)
	response = client.request(method_name="getbalance", uid=uid)
	print(response)
	print("----------------------------------------------------------------------")


##################################################################################
						# Make offer by buyer for seller
def make_offer_from_buyer_to_seller(cid):
	print("\n[+] -- Make offer for seller")
	time.sleep(1)
	public_key = "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"
	private_key = "1ebaa1c3b723a04cfbcdc39bebaebac23da71b5f4f95607d0793958b993d758f"
	
	message = json.dumps({
			"cid":cid,
			"buyer_access_string":public_key,
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/offer" % public_key)
	print("Request to url: " + url)
	time.sleep(2)
	request = requests.post(url, data=data)
	print(request.text)
	

	print("-----------------------------------------------------------------------")

##################################################################################
						# Make offer by buyer for seller
def make_offer_from_buyer_to_seller_with_price(cid, price):
	print("\n[+] -- Make offer for seller")
	time.sleep(1)
	public_key = "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"
	private_key = "1ebaa1c3b723a04cfbcdc39bebaebac23da71b5f4f95607d0793958b993d758f"
	
	message = json.dumps({
			"cid":cid,
			"buyer_access_string":public_key,
			"offer_price":price,
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/offer" % public_key)
	print("Request to url: " + url)
	time.sleep(2)
	request = requests.post(url, data=data)
	print(request.text)
	

	print("-----------------------------------------------------------------------")





###################################################################################
						# Accept offer by seller

def accept_offer_from_buyer(cid, suid, buid):
	print("\n[+] -- Accepting offer from buyer")
	time.sleep(1)
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	email = "denis@mail.ru"
	device_id = "lenovo"
	message = json.dumps({
			"cid":cid,
			"buyer_access_string": "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310",
			"buyer_pubkey":"04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310",
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/deal" % public_key)
	print("Request to: " + url)
	time.sleep(2)
	print("\nBalances before deal.")
	client = HTTPClient(settings.balanceurl)
	sellerbalance = client.request(method_name="getbalance", uid=suid)
	buyerbalance = client.request(method_name="getbalance", uid=buid)

	request = requests.post(url, data=data)
	print(request.text, "\n")
	# Check balances
	print("\nBalances after deal.")
	sellerbalance = client.request(method_name="getbalance", uid=suid)
	buyerbalance = client.request(method_name="getbalance", uid=buid)
	print(sellerbalance[str(suid)])
	print(buyerbalance[str(buid)])


################################################################################
					# Reject offer
	
def reject_offer_by_owner(cid):
	print("\n[+] -- Rejecting offer by seller")
	time.sleep(1)
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	message = json.dumps({
		"offer_id":{
			"cid":cid,
			"buyer_addr":Qtum.public_key_to_hex_address("04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"),
			},
			"timestamp": get_time_stamp(),
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/offer" % public_key)
	print("Request to: " + url)
	time.sleep(2)

	request = requests.put(url, data=data)
	print(request.text, "\n")


################################################################################
					# Reject offer
	
def reject_offer_by_buyer(cid):
	print("\n[+] -- Rejecting offer by buyer")
	time.sleep(1)
	public_key = "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"
	private_key = "1ebaa1c3b723a04cfbcdc39bebaebac23da71b5f4f95607d0793958b993d758f"
	message = json.dumps({
		"offer_id":{
			"cid":cid,
			"buyer_addr":Qtum.public_key_to_hex_address("04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"),
			},
			"timestamp": get_time_stamp(),
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/blockchain/%s/offer" % public_key)
	print("Request to: " + url)
	time.sleep(2)

	request = requests.put(url, data=data)
	print(request.text, "\n")



###############################################################################
							# Get all content

def get_all_content():							
	#url = "%s:%s%s" % (settings.host, settings.pmesport, 
	#					settings.ENDPOINTS["allcontent"])
	url = "http://127.0.0.1:8000/api/blockchain/content"
	print(url)
	request = requests.get(url)
	print(request.text)





"---------------------------------------------------------------------------------"
if __name__ == '__main__':
	from test_news import *
	"""
	#
	# Create testing balance table
	
	client = pymongo.MongoClient()
	balance_db = client[settings.DBNAME]
	balance = balance_db[settings.BALANCE]

	accounts_db = client[settings.DBNAME]
	accounts = accounts_db[settings.ACCOUNTS]
	accounts.remove()
	# Clear testing tables
	balance.remove()
	client.pmes.autoincrement.remove()
	accounts_db[settings.WALLET].remove()
	accounts_db[settings.NEWS].remove()
	"""



	cid = 82
	price=4
	inc = 20
	hash_="QmTwUP3wPsQ7LGhTrPnXFBEWSc4xrJB7ZFnfhq687AQnuY"

	#create_account_with_valid_data()
	#increment_buyers_balance(inc, 2)
	#create_account_with_existing_data()
	#create_account_with_invalid_data1()
	#create_account_with_invalid_data2()
	#write_data_to_blockchain()
	#write_invalid_data_to_blockchain()
	#get_data_from_blockchain(hash_=hash_)

	#setprice_for_content(cid=cid, price=price)
	#create_buyer_with_valid_data()
	#increment_buyers_balance(inc, 3)
	#make_offer_from_buyer_to_seller(cid=cid)
	#make_offer_from_buyer_to_seller_with_price(cid=cid, price=13)
	#getaccountdata()
	#get_news_for_seller()
	#accept_offer_from_buyer(cid,2,3)
	#reject_offer_by_owner(cid)
	#reject_offer_by_buyer(cid)
	#get_all_content()
