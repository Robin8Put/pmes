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

"""
# Try to repeat creating
valid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=valid_data)
print(request.text)

# Create new account with invalid signature
valid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eaef217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=valid_data)
assert request.status_code == 403



# Create new account without public key
invalid_data1 = {
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=invalid_data1)
assert request.status_code == 403




# Create new account without signature
invalid_data1 = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"message":"aaa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=invalid_data1)
assert request.status_code == 403

# Create new account without message
invalid_data1 = {
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"email":"denis@mail.ru",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=invalid_data1)
assert request.status_code == 403

# Create new account with public key, signature, message
#			and without all required fields
invalid_data = {
	"public_key":"04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa",
	"signature":"304402201ccb4679cfc8221b542996799579eacf217b80caf77b1351f82630e31af914df022054e3eddca9d465c27cc1aab3977547d04a9ffa8b3adf490356265da68afb2554",
	"message":"aaa",
	"device_id":"kjhlkj"
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
									data=invalid_data)
assert request.status_code == 400

# Get balance
request = requests.get("http://127.0.0.1:%s/api/accounts/04be7fc91026eeff5c3ad93b800a457aeab1b5fb494d8797f47a4519f47d8ee8d0c12973892bdd48877a66e549ab3f53b0eb768e082b1273610e1eb6a7718e78fa/balance" % settings.pmesport)
print(request.json())
"""


# Get accounts data
request = requests.get("http://127.0.0.1:%s/api/accounts/04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156" % settings.pmesport,
	                    params=data1)
assert "denis@mail.ru" == request.json()["email"]


request = requests.get("http://127.0.0.1:%s/api/accounts/040c07e377168074f29df2838526322516e34591ddb6bf7ca74cbdf03435a176e039fc4960352e551ed0ed5f252503bcd4e8b6dc44e8ad018baff473860a6999bc" % settings.pmesport,
	                    params=data2)
assert "artem@mail.ru" in request.json()["email"]


message = json.dumps({
	"cid":1,
	"price":23,
	"timestamp": get_time_stamp()
})

dataforsetprice = {
	"message":message,
	"public_key":public_key,
	"signature":Bip32Keys.sign_message(message, private_key),
}

request = requests.post("http://127.0.0.1:%s/api/blockchain/data/price" % settings.pmesport, data=dataforsetprice)

print(request.json()) 


request = requests.get("http://127.0.0.1:%s/api/blockchain/data/price" % settings.pmesport, params={"cid":1})

print(request.json())