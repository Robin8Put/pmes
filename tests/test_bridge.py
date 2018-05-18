from tornado_components.rpc_client import RPCClient
from jsonrpcclient.http_client import HTTPClient
from tornado_components.timestamp import get_time_stamp
import requests

#bridge_host = "http://192.168.1.99:8888"
bridgehost = "http://127.0.0.1:8003/api/bridge"
storagehost = "http://127.0.0.1:8001/api/storage"
balancehost = "http://127.0.0.1:8004/api/balance"


if __name__ == '__main__':

	
	#RPCClient.lastblockid(bridge_host)
	#RPCClient.data_from_blockchain(bridge_host, {"cid":1})
	#RPCClient.data_from_blockchain(bridge_host, {"hash":"QmeexEUxvw638e1VriqLtQbPTnH3AAy5vkjK73yMVhfybY"})
	#RPCClient.getownerbycid(bridge_host,{"cid":1000})
	#RPCClient.getcontentdescr(bridge_host, {"cid":1})

	#data = {
	#	"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
	#	"cus":"3big5 cusok"
	#}

	
	#RPCClient.postcontent(bridge_host,data)
	#RPCClient.setdescrforcid(bridge_host, {"cid":1, "descr":"my description"})
	#RPCClient.last_access_string(bridge_host, {"cid":1})
	#data = {
	#	"cid":11,
	#	"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
	#	"access_string": "access",
	#	"new_owner":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	#}
	#RPCClient.changeowner(bridge_host, data)
	#data = {
	#	"cid":11,
	#	"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
	#	"access_string": "access",
	#	"buyer_pubkey":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	#}
	#RPCClient.sellcontent(bridge_host, data)
	#client = HTTPClient(bridge_host)

	#data = {"cus":"morning minor tests", "owneraddr":"fdc1ae05c161833cdf135863e332126e15d7568c"}
	#client.request(method_name="makecid", **data)

	#data={"cid":1, "price":1000}
	#RPCClient.setprice(bridge_host, data)

	#data={"cid":1}
	#RPCClient.getprice(bridge_host, data)

	
	data = {"cid":1, 
			"buyer_pubkey":"04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156",
			"buyer_access_string":"04e2a4c921001b7510cf9a499fba3e6147a73a977196cbffd9ad863171b95a089ddedaf8231e842ff2be63be926ca345836a7edc3d5e098bdeb0a2ff7ddca7f156"}
	print(RPCClient.makeoffer(storagehost, balancehost, bridgehost, data))
	#client = HTTPClient(storagehost, balancehost % data["buyer_pubkey"], bridgehost)
	#print(client.request(method_name="make_offer", **data))

	#data = {"cid":2, "buyer_addr":"fdc1ae05c161833cdf135863e332126e15d7568c"}
	#RPCClient.rejectoffer(bridge_host, data)
