import json
import logging

with open('settings.json') as f:
    config = json.load(f)

blockchain = config['blockchain']

blockchain_type = blockchain['type']
blockchain_host = blockchain['host']
blockchain_port = int(blockchain['port'])
contract_owner = blockchain['contract_owner']
contract_owner_hex = blockchain['contract_owner_hex']
contract_address = blockchain['contract_address']
decimals = int(blockchain['decimals'])
blockchain_username = blockchain['credentials']['username']
blockchain_password = blockchain['credentials']['password']

storage = config['storage']
storage_type = storage['type']
storage_host = storage['host']
storage_port = int(storage['port'])
storage_download_time_limit = storage['download_time_limit']

api_key = config['api_key']

