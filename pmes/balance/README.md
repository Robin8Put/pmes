# Robin8 BlockChain Balance module

This API provides access to functionality for adding wallet, checking and changing its balance state

## Installation

Clone sources from git:

```bash
git clone https://bitbucket.org/robin8_put/balance.git
```

Create virtualenv and install needed libraries from the requirements.txt:

```bash
cd libs
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Description

This module allows:

- add wallets to user account
- increment / decrement balance in the wallet
- check wallets and amount of coins on them

View API details in the file [Robin8_BlockChain_BALANCE_API.docx](Robin8_BlockChain_BALANCE_API.docx).

And DB schema in the [Robin8_BlockChain_BALANCE_DB.docx](Robin8_BlockChain_BALANCE_DB.docx).

