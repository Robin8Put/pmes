# Coin module

This module parses blockchain transactions to find our wallets and synchronize amount of money in blockchain with wallets in our system.

Now coin module works with Qtum transactions.

## Installation

Create virtualenv and install needed libraries from the `requirements.txt`:

```bash
cd coin
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Running COIN module

For running daemon use next commands:

```
python one_coin.py start  --- start daemon
python one_coin.py stop  --- stop daemon
python one_coin.py restart  --- restart daemon
```
