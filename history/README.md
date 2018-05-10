# History module

This API provides functionality to save logs about actions and history of transactions.

This module allows:

- save logs about actions and history of transactions
- retrieve old data

View API details in the file [Robin8_BlockChain_HISTORY_API.md](Robin8_BlockChain_HISTORY_API.md).

## Installation

This module contains two different submodules:

- for working with MongoDB
- for working with ClickHouse. Doesn't allow delete or update saved data

Select needed submodule and continue instalation.

Create virtualenv and install needed libraries from the requirements.txt:

```bash
cd history/submodule
virtualenv --python=python3.6 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Running History module

For running History module execute next command:

```bash
python3 main.py
```
