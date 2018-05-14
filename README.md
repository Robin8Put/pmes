# Profile Management EcoSystem

Profile Management EcoSystem (PMEC) provides next functionality:

- get content from the blockchain
- set content in the blockchain
- get content description from the blockchain
- set content description in the blockchain
- change owner of data
- sell content

View API details in the file [Robin8_BlockChain_PDMS_API.md](pdms/Robin8_BlockChain_PDMS_API.md).

This repository contains the following modules:

1. **ams** - manage user's accounts (registration, authorization, profile management)
2. **balance** - provide work with wallets (add wallets, view/increment/decrement balance in the wallet)
4. **bip32keys** - utilities used for simplifying communication with crypto-libraries
3. **history** - save logs about actions and history of transactions
5. **mail** - save and send mails
6. **pdms** - Profile Data Management System (PDMS). COntains **qtum_bridge** that provides access to information of Robin8 Smart Contract based on Qtum BlockChain

## Installation

Clone sources from git:

```bash
git clone https://github.com/Robin8Put/pmes.git
```

Create virtualenv and install needed libraries from the `requirements.txt`:

```bash
cd pmes
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Modules installations were described into appropriate readmes.


PMES works with four modules: AMS, balance, pdms and qtum_bridge.

Therefore, for running application you should run 4 servers:

1. **ams** server:

```bash
source venv/bin/activate
python3 ams/main.py
```

2. **balance** server:

```bash
source venv/bin/activate
python3 balance/balance_api.py
```

3. **bridge** server:

```bash
source venv/bin/activate
python3 pdms/bridge/index.py
```

4. **pdms** server:

```bash
source venv/bin/activate
python3 pdms/main.py
```


## How to use PMES

For using Profile Management EcoSystem:

1. Run [PDMS module](https://github.com/Robin8Put/pmes/tree/master/pdms)
2. Run [Python mock client](https://github.com/Robin8Put/pdms_py_client)
3. Create client object
	- registration
	- authorization
4. Then you can use mectioned functionalities

# Additional resources:  
The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification) 

# License

The Robin8 Profile Management EcoSystem and all modules are released under the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).