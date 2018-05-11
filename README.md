# Profile Management EcoSystem

Profile Management EcoSystem (PMEC) provides next functionality:

- get content from the blockchain
- set content in the blockchain
- get content description from the blockchain
- set content description in the blockchain
- change owner of data
- sell content

View API details in the file [Robin8_BlockChain_PDMS_API.md](pdms/Robin8_BlockChain_PDMS_API.md).

## Installation

Clone sources from git:

```bash
git clone https://github.com/Robin8Put/pmes.git
```

## Running

For running module you should run server by using next:

```bash
python3 main.py
```

## How to use PMES

For using Profile Management EcoSystem:

1. Run [PDMS module](https://github.com/Robin8Put/robin8_blockchain/tree/master/pdms)
2. Run [mock client](https://github.com/Robin8Put/robin8_blockchain/tree/master/mock_clients)
3. Create client object
	- registration will be done inside the system if user doesn't have profile
	- authorization will be done inside the system if user have profile
4. Then you can:
	- save data in blockchain
	- get data from blockchain
	- get data owner wallet address
	- set/get data description

# Additional resources:  
The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification) 

# License

The Robin8 Profile Management EcoSystem and all modules are released under the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).