import client
from tornado_components import rpc_client
from jsonrpcclient.http_client import HTTPClient 

storagehost = "http://127.0.0.1:8001/api/storage"
balancehost = "http://127.0.0.1:8004/api/balance"
bridgehost = "http://127.0.0.1:8003/api/bridge"


client = client.PMESClient()

#                           Create seller
#client.gen_keys()
#client.fill_form()
#print(client.create_account())
#print(client.get_account_data())
#b = HTTPClient(balancehost)
#b.request(method_name="incbalance", uid=, amount=)
#print(client.post_data_to_blockchain())
#print(client.get_data_from_blockchain())
#print(client.setprice())
# Save wallet data, balance, cid


#                           Create buyer
#client.gen_keys()
#client.fill_form()
#print(client.create_account())
#c = HTTPClient(balancehost)
#c.request(method_name="incbalance", uid=, amount=)
#print(client.get_account_data())
# Save wallet data, balance


#                           Offer
#makeofferdata = {
#	"buyer_pubkey":"",
#	"buyer_access_string":"",
#	"cid":
#}
#print(rpc_client.RPCClient.makeoffer(storagehost, balancehost, bridgehost, makeofferdata))
	
	
#acceptofferdata = {
#	"public_key":"",
#	"buyer_access_string":"",
#	"buyer_pubkey":"",
#	"cid":
#}
#print(rpc_client.RPCClient.acceptoffer(storagehost, balancehost, bridgehost, acceptofferdata))
	



#                           Check
#c = HTTPClient(balancehost)
#print(c.request(method_name="getbalance", uid=))  #seller
#print(c.request(method_name="getbalance", uid=3))  # buyer
