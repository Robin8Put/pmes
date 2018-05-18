import requests
import sys
import os
import random
import json
import pymongo
import time
import datetime
from tornado_components import mongo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings
from bip32keys.bip32keys import Bip32Keys

table = mongo.Table(dbname="pmes", collection="accounts")
client = pymongo.MongoClient('localhost', 27017)
db = client.address_balance
accounts = db.accounts
table.collection.remove()
accounts.remove()


def get_time_stamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')


public_key = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
private_key = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
email = "denis@mail.ru"
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


request = requests.get("http://127.0.0.1:%s/api/blockchain/lastblockid" % settings.pmesport)
print(request.json())

params = {"hash":"QmeexEUxvw638e1VriqLtQbPTnH3AAy5vkjK73yMVhfybY"}
request = requests.get("http://127.0.0.1:%s/api/blockchain/data" % settings.pmesport, 
								params=params)
print(request.json())

params = {"cid":1}
request = requests.get("http://127.0.0.1:%s/api/blockchain/owner" % settings.pmesport, 
								params=params)
print(request.json())

params = {"cid":1}
request = requests.get("http://127.0.0.1:%s/api/blockchain/description" % settings.pmesport, 
								params=params)
print(request.json())

r = lambda: random.choice(range(1000))
data.update({"cus":"cusok" + str(r)})
request = requests.post("http://127.0.0.1:%s/api/blockchain/data" % settings.pmesport, 
								data=data)
print(request.json())

d0 = data
d0.update({"cid":1, "descr":"my description"})
request = requests.post("http://127.0.0.1:%s/api/blockchain/description" % settings.pmesport, 
								data=d0)
print(request.json())

params = {"cid":1}
request = requests.get("http://127.0.0.1:%s/api/blockchain/access_string" % settings.pmesport, 
								params=params)
print(request.json())
print("\n")

d1 = data
d1.update({
		"cid":1,
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"access_string": "password",
		"new_owner":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	})
request = requests.put("http://127.0.0.1:%s/api/blockchain/owner" % settings.pmesport, 
									data=d1)
assert request.status_code == 404

d2 = data
d2.update({
		"cid":1,
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"access_string": "access",
		"buyer_pubkey":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	})
request = requests.post("http://127.0.0.1:%s/api/blockchain/sale" % settings.pmesport, 
									data=d2)
assert request.status_code == 403