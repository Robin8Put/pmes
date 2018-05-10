# Robin8 BlockChain

This repository contains the following app:

- Profile Data Management System (PDMS)

And next set of modules:

1. **ams** - manage user's accounts (registration, authorization, profile management)
2. **balance** - provide work with wallets (add wallets, view/increment/decrement balance in the wallet)
3. **history** - save logs about actions and history of transactions
4. **libs** - utilities used for simplifying communication with crypto-libraries
5. **mock_clients** - sample of client
6. **pdms** - Profile Data Management System (PDMS)
7. **qtum_bridge** - provide access to information of Robin8 Smart Contract based on Qtum BlockChain

## Installation

Clone sources from git:

```bash
git clone https://github.com/Robin8Put/pdms.git
```

Modules installations were described into appropriate readmes.

## How to use Profile Data Management System (PDMS)

For using Profile Data Management System:

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

