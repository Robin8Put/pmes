from jsonrpcclient.http_client import HTTPClient 


client = HTTPClient("http://127.0.0.1:8001/api/storage")

data = {"cid":89, "buyer_addr":"66ca783b8a37ea00d872559c612b5d6b650263e5",
		"price":890}


a = client.request(method_name="removeoffer", **data)

print(a)
