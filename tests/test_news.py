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



def get_time_stamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')



def send_news_to_seller(cid):
	public_key = "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"
	owneraddr = "66ca783b8a37ea00d872559c612b5d6b650263e5"
	access_string = "04e78671c682ad58fb746dd24275db0e9d693dea80a6471faf598e444cbfe9e88e0653c273f36b5ac474c2d7c9d5048c2395a43820a7e1b044d25d18483e36b310"
	data = {
		"event_type":"made offer",
		"cid":cid,
		"access_string":access_string,
		"buyer_pubkey":public_key,
		"owneraddr":owneraddr
	}
	client = HTTPClient(settings.storageurl)
	response = client.request(method_name="setnews", **data)
	return response


def get_news_for_seller():
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
	print("---------------------------------------------------------------------")
	print("\n[+] -- Getting news for seller")
	time.sleep(1)
	url = "%s:%s%s" % (settings.host, settings.pmesport, 
						"/api/accounts/%s/news" % public_key)
	print("Request to:   " + url)
	time.sleep(2)
	message = json.dumps({
			"timestamp": get_time_stamp()
		})
	data = {
		"message": message,
		"public_key": public_key,
		"signature": Bip32Keys.sign_message(message, private_key)
	}
	request = requests.get(url, params=data)
	print(request.text)


def getaccountdata():
	public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
	print("---------------------------------------------------------------------")
	print("\n[+] -- Receiving account data")
	time.sleep(1)
	url = "%s:%s%s/%s" % (settings.host, settings.pmesport, 
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


#send_news_to_seller(170)
#get_news_for_seller()
#getaccountdata()


