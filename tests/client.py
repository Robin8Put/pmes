# Endpoints  
		# /api/accounts
		# /api/accounts/([a-zA-Z0-9]+?)
		# /api/accounts/([a-zA-Z0-9]+?)/profiles
		# /api/blockchain/([a-zA-Z0-9]+?)/([a-zA-Z0-9]+?)/reviews
		# /api/blockchain/([a-zA-Z0-9]+?)/review
		# /api/blockchain/([a-zA-Z0-9]+?)/deal
		# /api/blockchain/([a-zA-Z0-9]+?)/deals
		# /api/accounts/([a-zA-Z0-9]+?)/output-offers
		# /api/accounts/([a-zA-Z0-9]+?)/input-offers
		# /api/blockchain/([a-zA-Z0-9]+?)/write-access-offer
		# /api/blockchain/([a-zA-Z0-9]+?)/read-access-offer
		# /api/accounts/([a-zA-Z0-9]+?)/news
		# /api/blockchain/profile
		# /api/blockchain/([0-9]+)/description
		# /api/blockchain/([0-9]+)/price
		# /api/blockchain/([a-zA-Z0-9]+?)/([a-zA-Z0-9]+?)/profile

import requests
import json
import random
import string
from pprint import pprint
from pymongo import MongoClient
from jsonrpcclient.http_client import HTTPClient


create_account_url = "http://190.2.149.83/api/accounts/"
get_account_url = "http://190.2.149.83/api/accounts/%s/"
get_account_profiles_url = "http://190.2.149.83/api/accounts/%s/profiles/"
post_data_url = "http://190.2.149.83/api/blockchain/%s/%s/profile/"
put_descr_url = "http://190.2.149.83/api/blockchain/%s/description/"
put_write_price_url = "http://190.2.149.83/api/blockchain/%s/price/"
post_writeaccess_offer_url = "http://190.2.149.83/api/blockchain/%s/write-access-offer/"
post_readaccess_offer_url = "http://190.2.149.83/api/blockchain/%s/read-access-offer/"
get_output_offers_url = "http://190.2.149.83/api/accounts/%s/output-offers/"
post_QTUM_deal_url = "http://190.2.149.83/api/blockchain/%s/deal/"
post_QTUM_review_url = "http://190.2.149.83/api/blockchain/%s/review/"
get_account_shared_profiles_url = "http://190.2.149.83/api/blockchain/%s/deals/"
get_single_content_url = "http://190.2.149.83/api/blockchain/%s/%s/profile/"


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


def post_buyer():

	with open("generated.json") as keys:
		keys_list = json.load(keys)

	public_key = random.choice(keys_list)["public_key"]
	

	message = {
				"device_id": "device_id"
			}
		
	data = {
		"message": message,
		"public_key": public_key
	}
	print(create_account_url)
	response = requests.post(create_account_url, data=json.dumps(data))

	pprint(response.text)

	with open("currentbuyer.json", "w") as current:
		current.write(json.dumps({"public_key":public_key, "id":response.json()["id"]}))


def post_seller():

	with open("generated.json") as keys:
		keys_list = json.load(keys)

	public_key = random.choice(keys_list)["public_key"]
	

	message = {
				"device_id": "device_id"
			}
		
	data = {
		"message": message,
		"public_key": public_key
	}
	response = requests.post(create_account_url, data=json.dumps(data))

	pprint(response.json())

	with open("currentseller.json", "w") as current:
		current.write(json.dumps({"public_key":public_key, "id":response.json()["id"]}))


def delete_currents():
	client = MongoClient().pmes.accountso

	with open("currentbuyer.json") as file:
		buyer = json.load(file)
		try:
			client.delete_one({"public_key":buyer["public_key"]})
		except:
			pass

	with open("currentbuyer.json", "w") as file:
		file.write(json.dumps({}))

	with open("currentseller.json") as file:
		seller = json.load(file)
		try:
			client.delete_one({"public_key":seller["public_key"]})
		except:
			pass

	with open("currentseller.json", "w") as file:
		file.write(json.dumps({}))


	print("Done")


def get_buyers_account():
	with open("currentbuyer.json") as file:
		public_key = json.load(file)["public_key"]

	response = requests.get(get_account_url % public_key)
	pprint(response.json())	


def get_sellers_account():
	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]


	print(get_account_url % public_key)
	response = requests.get(get_account_url % public_key)
	pprint(response.text)	


def get_buyers_profiles():
	with open("currentbuyer.json") as file:
		public_key = json.load(file)["public_key"]

	response = requests.get(get_account_profiles_url % public_key)
	pprint(response.json())	
	return(response.json())
	

def get_buyers_shared_profiles():
	with open("currentbuyer.json") as file:
		public_key = json.load(file)["public_key"]

	response = requests.get(get_account_shared_profiles_url % public_key)
	pprint(response.json())	

def get_sellers_profiles():
	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	response = requests.get(get_account_profiles_url % public_key)
	pprint(response.json())	


def update_QTUM_cid():
	client = HTTPClient("http://localhost:8003/api/bridge")
	cid = client.request(method_name="get_next_cid")["next_cid"]
	content = list(MongoClient().QTUM.content.find())[-1]
	txid = content["txid"]
	MongoClient().QTUM.content.find_one_and_update(
							{"txid":txid},{"$set":{"cid":int(cid)-1}})
	print("Done")


def update_ETH_cid():
	client = HTTPClient("http://localhost:8007/api/bridge")
	cid = client.request(method_name="get_next_cid")["next_cid"]
	content = list(MongoClient().ETH.content.find())[-1]
	txid = content["txid"]
	MongoClient().ETH.content.find_one_and_update(
							{"txid":txid},{"$set":{"cid":int(cid)-1}})
	print("Done")


def post_data_to_qtum():
	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]



	message = {
		"cus": id_generator(),
		"description": id_generator(),
		"read_access": 1000 * 10**8,
		"write_access": 2000 * 10**8
	}

	data = {
		"message":message
	}

	url = post_data_url % (public_key, "ETH") 
	pprint(url)
	response = requests.post(url, data=json.dumps(data))

	pprint(response.text)


def incqtum(amount):
	with open("currentseller.json") as file:
		seller_id = json.load(file)["id"]

	with open("currentbuyer.json") as file:
		buyer_id = json.load(file)["id"]

	url1 = "http://190.2.149.83/api/accounts/%s/balance/" % seller_id
	url2 = "http://190.2.149.83/api/accounts/%s/balance/" % buyer_id

	r1 = requests.post(url1, data=json.dumps({"amount":amount, "coinid": "PUTTEST"}))
	r2 = requests.post(url2, data=json.dumps({"amount":amount, "coinid": "PUTTEST"}))

	print(r1.text)
	print(r2.text)


def inceth(amount):
	with open("currentseller.json") as file:
		seller_id = json.load(file)["id"]

	with open("currentbuyer.json") as file:
		buyer_id = json.load(file)["id"]

	url1 = "http://localhost:8000/api/accounts/%s/balance" % seller_id
	url2 = "http://localhost:8000/api/accounts/%s/balance" % buyer_id

	requests.post(url1, data=json.dumps({"amount":amount, "coinid": "ETH"}))
	requests.post(url2, data=json.dumps({"amount":amount, "coinid": "ETH"}))

	print("Done")


def put_QTUM_description(cid=None):
	if not cid:
		last_content = list(MongoClient().QTUM.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	description = id_generator()

	message = {
		"description":description,
		"coinid": "QTUM"
	}

	data = {
		"public_key":public_key,
		"message":message
	}

	response = requests.put(put_descr_url % cid, data=json.dumps(data))

	print(response.text)


def put_QTUM_write_price(cid=None):
	if not cid:
		last_content = list(MongoClient().QTUM.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	price = 1100 * 10**8

	message = {
		"price":price,
		"access_type":"write_price",
		"coinid": "QTUM"
	}

	data = {
		"public_key":public_key,
		"message":message
	}

	response = requests.put(put_write_price_url % cid, data=json.dumps(data))

	pprint(response.json())


def put_QTUM_read_price(cid=None):
	if not cid:
		last_content = list(MongoClient().QTUM.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	price = 2100 * 10**8

	message = {
		"price":price,
		"access_type":"read_price",
		"coinid": "QTUM"
	}

	data = {
		"public_key":public_key,
		"message":message
	}

	response = requests.put(put_write_price_url % cid, data=json.dumps(data))

	pprint(response.json())



def put_ETH_description(cid=None):
	if not cid:
		last_content = list(MongoClient().ETH.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	description = id_generator()

	message = {
		"description":description,
		"coinid": "ETH"
	}

	data = {
		"public_key":public_key,
		"message":message
	}

	response = requests.put(put_descr_url % cid, data=json.dumps(data))

	pprint(response.json())


def put_ETH_write_price(cid=None):
	if not cid:
		last_content = list(MongoClient().ETH.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	price = 123 * 10*8

	message = {
		"price":price,
		"access_type":"write_price",
		"coinid": "ETH"
	}

	data = {
		"public_key":public_key,
		"message":message
	}

	response = requests.put(put_write_price_url % cid, data=json.dumps(data))

	pprint(response.json())


def put_ETH_read_price(cid=None):
	if not cid:
		last_content = list(MongoClient().ETH.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		public_key = json.load(file)["public_key"]

	price = 123 * 10*8

	message = {
		"price":price,
		"access_type":"read_price",
		"coinid": "ETH"
	}

	data = {
		"public_key":public_key,
		"message":message
	}

	response = requests.put(put_write_price_url % cid, data=json.dumps(data))

	pprint(response.json())


def post_QTUM_writeaccess_offer(cid=None):
	if not cid:
		last_content = list(MongoClient().QTUM.content.find())[-1]
		cid = last_content["cid"]

	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	message = {
		"cid":cid,
		"coinid": "ETH",
		"buyer_access_string": buyer["public_key"]
	}

	data = {"message":message}

	response = requests.post(post_writeaccess_offer_url % buyer["public_key"],
														data=json.dumps(data))


	with open("currentoffer.json", "w") as file:
		offer = response.json()
		offer["coinid"] = "ETH"
		file.write(json.dumps(offer))

	pprint(offer)

def post_QTUM_readaccess_offer(cid=None):
	if not cid:
		last_content = list(MongoClient().QTUM.content.find())[-1]
		cid = last_content["cid"]

	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	message = {
		"cid":cid,
		"coinid": "QTUM",
		"buyer_access_string": buyer["public_key"]
	}

	data = {"message":message}

	response = requests.post(post_readaccess_offer_url % buyer["public_key"],
														data=json.dumps(data))


	with open("currentoffer.json", "w") as file:
		offer = response.json()
		offer["coinid"] = "QTUM"
		file.write(json.dumps(offer))

	pprint(offer)

def get_QTUM_buyers_offers():
	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	url = get_output_offers_url % buyer["public_key"]
	print(url)

	response = requests.get(url)

	pprint(response.text)



def put_QTUM_writeaccess_offer_by_buyer():

	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	with open("currentoffer.json") as file:
		offer = json.load(file)

	url = post_writeaccess_offer_url % buyer["public_key"]

	message = {
		"offer_id":{
			"cid":offer["cid"],
			"buyer_address":offer["buyer_address"]
		},
		"coinid":offer["coinid"]
	}
	data = {"message":message}

	response = requests.put(url, data=json.dumps(data))

	with open("currentoffer.json", "w") as file:
		file.write(json.dumps({}))

	pprint(response.json())


def put_QTUM_readaccess_offer_by_buyer():

	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	with open("currentoffer.json") as file:
		offer = json.load(file)

	url = post_readaccess_offer_url % buyer["public_key"]

	message = {
		"offer_id":{
			"cid":offer["cid"],
			"buyer_address":offer["buyer_address"]
		},
		"coinid":offer["coinid"]
	}
	data = {"message":message}

	response = requests.put(url, data=json.dumps(data))

	with open("currentoffer.json", "w") as file:
		file.write(json.dumps({}))

	pprint(response.json())


def post_QTUM_deal():
	with open("currentseller.json") as file:
		seller = json.load(file)

	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	with open("currentoffer.json") as file:
		offer = json.load(file)

	ident = {0:"read_access", 1:"write_access"}

	message = {
		"cid":offer["cid"],
		"buyer_access_string":buyer["public_key"],
		"buyer_pubkey":buyer["public_key"],
		"seller_access_string":"seller access string",
		"access_type": offer["offer_type"],
		"coinid": "ETH"
	}

	data = {"message":message}

	url = post_QTUM_deal_url % seller["public_key"]

	response = requests.post(url, data = json.dumps(data))

	pprint(response.json())


def post_QTUM_review():
	with open("currentseller.json") as file:
		seller = json.load(file)



	client = HTTPClient("http://localhost:8003/api/bridge")
	cid = client.request(method_name="get_next_cid")["next_cid"]

	message = {
		"cid":int(cid) - 1,
		"review":"very cool",
		"rating":5,
		"coinid":"QTUM"
	}

	data = {"message":message}

	url = post_QTUM_review_url % seller["public_key"] 

	response = requests.post(url, data=json.dumps(data))


def get_QTUM_input_offers(cid=None):
	if not cid:
		last_content = list(MongoClient().QTUM.content.find())[-1]
		cid = last_content["cid"]

	with open("currentseller.json") as file:
		seller = json.load(file)

	message = {
		"cid":cid,
		"coinid": "QTUM"
	}

	data = {"message":message}

	url = "http://localhost:8000/api/accounts/%s/input-offers" % seller["public_key"]

	response = requests.get(url, params={"message":json.dumps(message)})

	pprint(response.json())


def get_single_content():
	client = HTTPClient("http://localhost:8003/api/bridge")
	cid = client.request(method_name="get_next_cid")["next_cid"]
	cid = int(cid) - 1
	url = get_single_content_url % (cid, "QTUM")

	response = requests.get(url)

	pprint(response.json())



def make_review_by_buyer(cid):

	with open("currentbuyer.json") as file:
		buyer = json.load(file)

	message = {
		"cid":cid,
		"review":"cool review",
		"rating":5,
		"coinid":"ETH"
	}
	data = {"message":message}

	url = "http://190.2.149.83/api/blockchain/%s/review/" % buyer["public_key"]

	response = requests.post(url, data=json.dumps(data))
	print("\n\n")
	pprint(response.json())


def get_all_reviews(cid):


	url = "http://190.2.149.83/api/blockchain/%s/%s/reviews/" % (cid, "ETH")

	response = requests.get(url)

	pprint(response.json())


def get_all_content():
	url = "http://190.2.149.83/api/blockchain/profile/"

	response = requests.get(url)

	pprint(response.json())


def get_sellers_news():
	with open("currentseller.json") as file:
		seller = json.load(file)

	url = "http://localhost:8000/api/accounts/%s/news" % seller["public_key"]

	response = requests.get(url)

	pprint(response.json())

def withdrawQTUM():
	with open("currentseller.json") as file:
		seller = json.load(file)

	url = "http://190.2.149.83/api/accounts/withdraw"

	address = "qKoyDjof6F7sRFJcf9pq3TgA1ewW46rPD4"

	data = {
		"public_key": seller["public_key"],
		"signature":"signature",
		"message":{
			"coinid":"PUTTEST",
			"amount":10**8,
			"address":address,
			"timestamp":"timestamp",
			"recvWindow":5000
		}
	}

	response = requests.post(url, data=json.dumps(data))
	print(response.text)


def test():
	response = requests.get("http://190.2.149.83/api/accounts/test")
	print(response.text)



#########################################################################################




if __name__ == '__main__':
	from threading import Thread
	
	#incqtum(5000 * 10**8)

	#update_QTUM_cid()

	
	#post_buyer()
	#post_seller()
	#delete_currents()
	for i in range(2):
		t = Thread(target=get_buyers_account)
		t.start()
	#get_sellers_account()
	
	#get_buyers_profiles()
	#get_sellers_profiles()

	#get_buyers_shared_profiles()

	#post_data_to_qtum()

	#put_QTUM_description(cid=115)

	#put_QTUM_write_price(115)
	#put_QTUM_read_price()

	#post_QTUM_writeaccess_offer(cid=105)
	#post_QTUM_readaccess_offer(cid=119)

	#get_QTUM_buyers_offers()
	#get_QTUM_input_offers()

	#put_QTUM_writeaccess_offer_by_buyer()
	#put_QTUM_readaccess_offer_by_buyer()

	#post_QTUM_deal()

	#get_single_content(cid=106)

	#make_review_by_buyer(105)

	#get_all_reviews(105)
	
	#get_all_content()

	#get_sellers_news()

	#withdrawQTUM()

	#for i in range(1000):
	#	t = Thread(target=test)
	#	t.start()




