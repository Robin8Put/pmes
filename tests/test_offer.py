from jsonrpcclient.http_client import HTTPClient 


client = HTTPClient("http://127.0.0.1:8001/api/storage")

data = {"cid":89, "buyer_addr":"1ba5ef234bb4e26a71a977958e074edf2924d81f",
		"price":890}


a = client.request(method_name="removeoffer", **data)

print(a)