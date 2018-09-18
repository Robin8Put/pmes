import json
import logging

with open('eth_settings_mainnet.json') as f:
    config = json.load(f)

blockchain = config['blockchain']

blockchain_type = blockchain['type']
contract_owner = blockchain['contract_owner']
private_key = blockchain['private_key']
contract_owner_hex = blockchain['contract_owner_hex']
contract_address = blockchain['contract_address']
ipc_path = blockchain['ipc_path']
http_provider = blockchain['http_provider']
decimals = int(blockchain['decimals'])
abi_file_path = blockchain['abi_file_path']

storage = config['storage']
storage_type = storage['type']
storage_host = storage['host']
storage_port = int(storage['port'])
storage_download_time_limit = storage['download_time_limit']

gas_limit = int(config['billing']['gasLimit'])
gas_price = int(config['billing']['gasPrice'])

with open(abi_file_path, 'r') as abi_f:
    pmes_abi = abi_f.read()
