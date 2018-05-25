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
from jsonrpcclient.http_client import HTTPClient 



table = mongo.Table(dbname="pmes", collection="test_accounts")
client = pymongo.MongoClient('localhost', 27017)
db = client.address_balance
accounts = db.accounts
table.collection.remove()
accounts.remove()


def get_time_stamp():
        ts = time.time()
        return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M')

# Create new account with public key, signature and message

public_key1 = "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
private_key1 = "bde5a03e2547b1fe47029ae12a2a1c678223c85fb5f2714f7605cea85ea3ebc9"
email1 = "denis@mail.ru"
device_id1 = "lenovo"
message1 = json.dumps({
		"email": email1,
		"device_id": device_id1,
		"timestamp": get_time_stamp()
	})
data1 = {
	"message": message1,
	"public_key": public_key1,
	"signature": Bip32Keys.sign_message(message1, private_key1),
	"email":email1,
	"device_id":device_id1
}
request = requests.post("http://127.0.0.1:%s/api/accounts" % settings.pmesport, 
								data=data1)



# Set news for account
news_data = {
	"event_type":"made offer",
	"cid": 20,
	"access_string":"04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156",
	"buyer_pubkey": "04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"
}
news_client = HTTPClient(settings.storageurl)
response = news_client.request(method_name="setnews", **news_data)
print(response)
