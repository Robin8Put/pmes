# Robin8 BlockChain qtum_blockchain

This utilities used for reloading qtum rpc.

## Installation

Clone sources from git:

```bash
git clone https://bitbucket.org/robin8_put/qtum_blockchain.git
```

Create virtualenv and install needed libraries from the `requirements.txt`:

```bash
cd libs
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Description

- `qtum_blockchain` --- library for generating public / private keys / blockchain address
    - `qtum_blockchain` --- contain `Bip32Keys` class which allows 
        - `__init__` --- init class with `qtum_rpc` parameter. Execute `reload_rpc` inside
        - `reload_rpc` --- reload rpc
        - `get_lastblockid` --- return last block id
