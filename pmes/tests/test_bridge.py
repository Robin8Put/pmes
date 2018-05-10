from tornado_components.rpc_client import RPCClient
from jsonrpcclient.http_client import HTTPClient
from tornado_components.timestamp import get_time_stamp

bridge_host = "http://127.0.0.1:8004"



if __name__ == '__main__':

	
	RPCClient.lastblockid(bridge_host)
	RPCClient.data_from_blockchain(bridge_host, {"cid":1})
	RPCClient.data_from_blockchain(bridge_host, {"hash":"QmeexEUxvw638e1VriqLtQbPTnH3AAy5vkjK73yMVhfybY"})
	RPCClient.getownerbycid(bridge_host,{"cid":1})
	RPCClient.getcontentdescr(bridge_host, {"cid":1})

	data = {
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"cus":"3big5 cusok"
	}

	
	RPCClient.postcontent(bridge_host,data)
	RPCClient.setdescrforcid(bridge_host, {"cid":1, "descr":"my description"})
	RPCClient.last_access_string(bridge_host, {"cid":1})
	data = {
		"cid":11,
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"access_string": "access",
		"new_owner":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	}
	RPCClient.changeowner(bridge_host, data)
	data = {
		"cid":11,
		"public_key":"0466a8ab68b62dab986bbdc1962f0558f4f675da79347a30cf81633b38fa2aa2951a3a98ff56ba2fb3d0f198ccf6d5ff7574e2abd0f7607ae6d0fb73109b60588d",
		"access_string": "access",
		"buyer_pubkey":"042d9c525132bf04da11735c4231798a44e443af3713add4f4cccd3d29c9329437f8829b063ffd3f48fbe0fc31d796a1ab1ff961196d99b50fe89aced2450a9eaf"
	}
	RPCClient.sellcontent(bridge_host, data)
	