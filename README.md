# Profile Management EcoSystem

The PMES integrated with the Qtum BlockChain.

The Profile Management EcoSystem (PMEC) provides the following functionality:

- get a content from the blockchain
- set a content in the blockchain
- get a content description from the blockchain
- set a content description in the blockchain
- change a data owner
- sell a content

View API details in a file [Robin8_BlockChain_PMES_API.md](Robin8_BlockChain_PMES_API.md).

This repository contains the following modules:

1. **ams** - Account Management System - module that manages user's accounts. Has registration and authorization functionalities
2. **balance** - module that implements work with the blockchain wallets. For instance, adding wallets, view/increment/decrement wallet's balance
2. **billing** - module that contains fee estimation details
4. **utils/bip32keys** - utilities used for simplifying communications with crypto-algorithms
4. **coin** - module that parses blockchain transactions to find PMES wallets and synchronize amount of money in blockchain with wallets in PMES
3. **history** - module that saves logs about actions and history of transactions
5. **mail** - module that saves and sends emails
6. **pdms** - Profile Data Management System (PDMS) - module that coordinate interactions between servers and daemons. It contains **qtum_bridge** module - middleware between the PMES and the blockchain
7. **parser** - module that parses blockchain, catches blockchain transactions and changes state of the account at the server
8. **js client** provides utilities for generating public / private keys / blockchain address and sign / verify messages.

An installation and running of the PMES are described [here](Installation.md).

## How to use the PMES

For using the Profile Management EcoSystem:

1. Run the [PMES modules](Installation.md)
2. Run a [Python mock client](https://github.com/Robin8Put/pdms_py_client)
3. Create a client object and use mentioned functionalities as described in the python mock client

# Additional resources:

The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification) 

# License

The Robin8 Profile Management EcoSystem and all modules are released under the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).
