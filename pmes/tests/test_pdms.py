import requests


request = requests.get("http://127.0.0.1:8003/api/blockchain/lastblockid")
print(request.json())

params = {"hash":"QmeexEUxvw638e1VriqLtQbPTnH3AAy5vkjK73yMVhfybY"}
request = requests.get("http://127.0.0.1:8003/api/blockchain/data", params=params)
print(request.json())

params = {"cid":1}
request = requests.get("http://127.0.0.1:8003/api/blockchain/owner", params=params)
print(request.json())

params = {"cid":1}
request = requests.get("http://127.0.0.1:8003/api/blockchain/description", params=params)
print(request.json())

data = {
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"cus":"0ee3big1d2255 cusok"
	}
request = requests.post("http://127.0.0.1:8003/api/blockchain/data", data=data)
print(request.json())

data = {"cid":1, "descr":"my description"}
request = requests.post("http://127.0.0.1:8003/api/blockchain/description", data=data)
print(request.json())

params = {"cid":1}
request = requests.get("http://127.0.0.1:8003/api/blockchain/access_string", params=params)
print(request.json())
print("\n")

data = {
		"cid":1,
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"access_string": "password",
		"new_owner":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	}
request = requests.put("http://127.0.0.1:8003/api/blockchain/owner", data=data)
assert request.status_code == 404


data = {
		"cid":1,
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"access_string": "access",
		"buyer_pubkey":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	}
request = requests.post("http://127.0.0.1:8003/api/blockchain/sale", data=data)
assert request.status_code == 404