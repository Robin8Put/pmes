#requirements
sudo apt-get install python3.6-dev

# Robin8 BlockChain Bridge module

This API provides access to information of Robin8 Smart Contract based on Qtum BlockChain.

## Installation

Clone sources from git:

```bash
git clone https://bitbucket.org/robin8_put/qtum_bridge.git
```

Create virtualenv and install needed libraries from the requirements.txt:

```bash
cd libs
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Running Bridge module

For running application run bash command:

```bash
python3 'index.py'
```

## Description

This module allows:

- get id of current block in qtum blockchain (last block)
- returns data about the balance of the server wallet
- get data from ipfs by specified ipfs-hash
- reads data from the smart contract by specified CID (Content-ID)
- get owner address or description of the specified CID
- create new CID from specified CUS-data (Content-Unical-String data)

View API details in the file [Robin8_BlockChain_BRIDGE_API.docx](Robin8_BlockChain_BRIDGE_API.docx).
