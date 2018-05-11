# Account Management System module

This API provides access to Account Management System (AMS) module.

This module allows:

- create account
- get account data
- get user balance

View API details in the file [Robin8_BlockChain_AMS_API.md](Robin8_BlockChain_AMS_API.md).

## Running AMS module

AMS module consist of two parts:

1. **ams** - main module
2. **storage** - data storage

Therefore, for running AMS module you should run 2 servers:

1. **ams** server in the `/ams` directory
2. **storage** server in the `/ams/storage` directory

Each of servers should starting with command below from their directory:

```bash
python3 main.py
```
