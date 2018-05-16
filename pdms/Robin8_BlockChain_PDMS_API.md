# Robin8 BlockChain Profile Data Management System

This API provides access to information of Profile Data Management System (PDMS).

The API uses the REST API standard.

API-methods:

- [Get last block id](#get-last-block-id)

- [Get content from blockchain](#get-content-from-blockchain)

- [Upload content to blockchain](#upload-content-to-blockchain)

- [Get owner by cid](#get-owner-by-cid)

- [Change owner of data](#change-owner-of-data)

- [Get content description](#get-content-description)

- [Set content description for cid](#set-content-description-for-cid)

- [Get last access string](#get-last-access-string)

- [Sell content](#sell-content)

The following is a description of the API-methods:


## Get lastblock id

* **URL:** `/api/blockchain/lastblockid`

* **Method:** `GET`

* **URL params**

    None

* **Body params**

    None

* **Sample response**

    [json]

```bash
    {"lastblockid": "ff02d34ac0000002228c"}
```

* **Description**

    This method returns `id` of current block in qtum blockchain (last block).

    **!!! This parameter (lastblockid) is required to create api-requests that require authorization.**

    `blockid` is a last 7 chars of last block hash concatenated with last block number in hex-format.


## Get content from blockchain

* **URL:** `/api/blockchain/data/?cid=&hash=`

* **Method:** `GET`

* **URL params**

    **Required** one of the next parameters:

    `cid=[string]`

    `hash=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        “cid”: [string], 
        “data”: [string] , 
        “owner”: [string]
    }
```


## Upload content to blockchain

* **URL:** `/api/blockchain/data/`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

```bash
    {
        “public_key”: [string],   #  this is the user id, one who will pay for the transaction
        “message”: {
            “data”: [string],
            “timestamp”: [string]
        },
        “signature”: [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result" : {
            "txid" : "175541a6de7276ce5e1c1bf3fe7c12ebd8f55a0892263e13bed2e8f7b79f76ed",
            "sender" : "QQNJ1yL2h1YucDdfXkcoWf41WrbiXZGJma",
            "hash160" : "2949a0eefcc7b6aa648c0a4845fa68ed1d985dc5"
        },
        "hash" : "QmWSAu67FRCdKFkQDudcMdz9r6k8xocPkyitWqMEmYVB4z",
        "cus" : "Test string",
        "addr" : "QQNJ1yL2h1YucDdfXkcoWf41WrbiXZGJma",
        "owneraddr" : "QQNJ1yL2h1YucDdfXkcoWf41WrbiXZGJma",
        "owner_hex_addr" : "2949a0eefcc7b6aa648c0a4845fa68ed1d985dc5",
        "secret" : "feec34cbfc0124bb534c368fa5ed3274fc1e66e49d84f09a06a24ba575b374f6",
        "blockid" : "e5a4f701f886"
    }
```


## Get owner by cid

* **URL:** `/api/blockchain/owner/?cid=`

* **Method:** `GET`

* **URL params**

    **Required:**

    `cid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        "owner": " QQNJ1yL2h1YucDdfXkcoWf41WrbiXZGJma "
    }
```


## Change owner of data

* **URL:** `/api/blockchain/owner/`

* **Method:** `PUT`

* **URL params**

    None

* **Body params**

```bash
    {
        “public_key”: [string],
        “message”: {
            “cid”: [string],
            “new_owner_pubkey”: [string],
            “access_string”: [string],
            “timestamp”: [string]
        }
        “signature”: [string]
    }
```

* **Sample response**

    [json]

```bash
    {
        'result': [string], 
        'cid': [string], 
        'new_owner': [string], 
        'access_string': [string], 
        'prev_owner': [string], 
        'contract_owner_hex': [string]
    }
```


## Get content description

* **URL:** `/api/blockchain/description/?cid=`

* **Method:** `GET`

* **URL params**

    **Required:**

    `cid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        "description": "Test description1"
    }
```

* **Description**

    Return content description from blockchain


## Set content description for cid

* **URL:** `/api/blockchain/description/`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

```bash
    {
        “public_key”: [string],
        “message”: {
            “cid”: [string], 
            “descr”: [string],
            “timestamp”: [string],
        }
        “signature”: [string],
        “cid”: [string], 
        “descr”: [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result": {
            "txid": "15d21c852b2159e32d2c1657207e85b52dacd153763db2b653c87ff8b22bead9", 
            "sender": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis", 
            "hash160": "fdc1ae05c161833cdf135863e332126e15d7568c"
            }, 
        "cid": "68", 
        "descr": "descr", 
        "addr": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis"
    }
```  


## Get last access string

* **URL:** `/api/blockchain/access_string/?cid=`

* **Method:** `GET`

* **URL params**

    **Required:**

    `cid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        "access_string": "Access string"
    }
```

* **Description**

    Get last access string for content in debug purposes


## Sell content

* **URL:** `/api/blockchain/sale`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

```body
    {
        “public_key”: [string],
        “message”: {
            “cid”: [string],
            “buyer_pubkey”: [string],
            “access_string”: [string],
            “timestamp”: [string]
        }
        “signature”: [string]
    }
```


* **Sample response**

    [json]

```bash
    {
        'result': [string], 
        'cid': [string], 
        'buyer_addr': [string], 
        'access_string': [string], 
        'content_owner': [string], 
        'contract_owner_hex': [string]
    }
```

* **Description**

    Get last access string for content in debug purposes
