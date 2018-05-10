from jsonrpcclient.http_client import HTTPClient

history_host = "http://192.168.1.184:8002/api/history"

client = HTTPClient(history_host)

client.request(method_name="log", module="123", event="transaction initiation", table="SuccessfulTransactions", args=["awdaw"])

# client.request(method_name="select", table="SuccessfulTransactions", query="WHERE id = 1")

# client.request(method_name="drop", table="SuccessfulTransactions")
