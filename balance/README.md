# Robin8 BlockChain Balance module

This API provides access to functionality for adding wallet, checking and changing its balance state

## Installation

Create virtualenv and install needed libraries from the `requirements.txt`:

```bash
cd balance
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Running Balance module

For running module execute command below:

```bash
python3 balance_api.py
```

## Description

This module allows:

- add wallets to user account
- remove wallets from user account
- increment / decrement balance in the wallet
- check wallets and amount of coins on them

View API details in the file [Robin8_BlockChain_BALANCE_API.md](Robin8_BlockChain_BALANCE_API.md).

And DB schema in the [Robin8_BlockChain_BALANCE_DB.docx](Robin8_BlockChain_BALANCE_DB.docx).

