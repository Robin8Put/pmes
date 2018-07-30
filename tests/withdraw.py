import requests
import json
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(base_dir)

from utils.bip32keys import bip32addresses

structure = {
	"withdraw": {
		"params": [{
			"public_key": "046990d393c3c9441f427d4d416809d1b17920740cadc1374e12b7bf5028786922612fbbb918f28c7ea4ec91ea0857a6643bde725303720f77936df8225ef8f34b",
			"message": {
				"timestamp": "",
				"recvWindow": "",
				"coinid": "BTC",
				"amount": 1000000,
				"address": "mxaMABiVqfHmngervojVxrNDLw7kZjBfU8"	
				},
			"signature": ""			
			},
	     {
			"public_key": "046990d393c3c9441f427d4d416809d1b17920740cadc1374e12b7bf5028786922612fbbb918f28c7ea4ec91ea0857a6643bde725303720f77936df8225ef8f34b",
			"message": {
				"timestamp": "",
				"recvWindow": "",
				"coinid": "BTCTEST",
				"amount": 100,
				"address": "mxaMABiVqfHmngervojVxrNDLw7kZjBfU8"	
			},
			"signature": ""			
		}]
    }
}
address = bip32addresses.Bip32Addresses.address_to_hex(
				"qena74SL4qiiRnvFQsTWYm6nZzQBaAuWGA")

data2 = {
			"public_key": "04775742c1dc83e27b243abf62ef4609374abf4fa0d3a7b4d38ad2cee31d61219f947fc6ce46029319ffd6754c60ed99903ec144155440eee761519a67eec08a52",
			"message": {
				"timestamp": "timestamp",
				"recvWindow": "recvWindow",
				"coinid": "QTUMTEST",
				"amount": 0.005*pow(10,8),
				"address": "qena74SL4qiiRnvFQsTWYm6nZzQBaAuWGA"
				},
			"signature": "signature"			
			}

response = requests.post("http://localhost:8000/api/accounts/withdraw", data=json.dumps(data2))
print(response.text)