import requests
from tornado_components import mongo
import pymongo
from bip32keys.bip32keys import Bip32Keys
import time
import datetime
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings

table = mongo.Table(dbname="pmes", collection="accounts")
client = pymongo.MongoClient('localhost', 27017)
db = client.address_balance
accounts = db.accounts
table.collection.remove()
accounts.remove()


def get_time_stamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')

# Create new account with public key, signature and message

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


request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
								data=data1)

assert isinstance(request.json(), dict)
assert "public_key" in request.json().keys()
assert "id" in request.json().keys()
assert "count" in request.json().keys()
assert "level" in request.json().keys()
assert "email" in request.json().keys()
assert "device_id" in request.json().keys()
assert "href" in request.json().keys()
assert "balance" in request.json().keys()


# Create another account with public key, signature and message

public_key = "040c07e377168074f29df2838526322516e34591ddb6bf7ca74cbdf03435a176e039fc4960352e551ed0ed5f252503bcd4e8b6dc44e8ad018baff473860a6999bc"
private_key = "914b4eb0e7e89eb04f564527d0b4d2453e0b5958830318b3fc40a3da356e4fd9"
email = "artem@mail.ru"
device_id = "hp"
message = json.dumps({
		"email": email,
		"device_id": device_id,
		"timestamp": get_time_stamp()
	})


data2 = {
	"message": message,
	"public_key": public_key,
	"signature": Bip32Keys.sign_message(message, private_key),
	"email":email,
	"device_id":device_id
}


request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=data2)

assert isinstance(request.json(), dict)
assert "public_key" in request.json().keys()
assert "id" in request.json().keys()
assert "count" in request.json().keys()
assert "level" in request.json().keys()
assert "email" in request.json().keys()
assert "device_id" in request.json().keys()
assert "href" in request.json().keys()
assert "balance" in request.json().keys()


# Try to create a new account with existing public key

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


request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=data1)

assert request.status_code == 400


# Get accounts data
request = requests.get("http://127.0.0.1:%s/api/accounts/04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156" % settings.pmesport,
	                    params=data1)
assert "denis@mail.ru" == request.json()["email"]


request = requests.get("http://127.0.0.1:%s/api/accounts/040c07e377168074f29df2838526322516e34591ddb6bf7ca74cbdf03435a176e039fc4960352e551ed0ed5f252503bcd4e8b6dc44e8ad018baff473860a6999bc" % settings.pmesport,
	                    params=data2)
assert "artem@mail.ru" in request.json()["email"]


message = json.dumps({
		"timestamp": get_time_stamp()
	})
data = {
	"message": message,
	"public_key": public_key,
	"signature": Bip32Keys.sign_message(message, private_key)
}

request = requests.get("http://127.0.0.1:%s/api/accounts/040c07e377168074f29df2838526322516e34591ddb6bf7ca74cbdf03435a176e039fc4960352e551ed0ed5f252503bcd4e8b6dc44e8ad018baff473860a6999bc/news" % settings.pmesport,
	                    params=data)
