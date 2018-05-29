# qtum_blockchain module

This utilities used for reloading qtum rpc.

- `qtum_blockchain` --- library for generating public / private keys / blockchain address
    - `qtum_blockchain` --- contain `Bip32Keys` class which allows 
        - `__init__` --- init class with `qtum_rpc` parameter. Execute `reload_rpc` inside
        - `reload_rpc` --- reload rpc
        - `get_lastblockid` --- return last block id
