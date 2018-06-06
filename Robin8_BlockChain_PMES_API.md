# Robin8 BlockChain Profile Management EcoSystem

This API provides access to information of Profile Management EcoSystem (PMES).

The API uses the REST API standard.

Now host is here: http://pdms.robin8.io.

API-methods:

- [Create new account](#create-new-account)

- [Get account data](#get-account-data)

- [Get last news for the account](#get-last-news-for-the-account)

- [Get content from the blockchain](#get-content-from-the-blockchain)

- [Post content to the blockchain](#post-content-to-the-blockchain)

- [Get description of content by cid](#get-description-of-content-by-cid)

- [Set description of content for cid](#set-description-of-content-for-cid)

- [Get content price](#get-content-price)

- [Set content price](#set-content-price)

- [Make offer for buying the content](#make-offer-for-buying-the-content)

- [Accept offer](#accept-offer)

- [Reject offer from buyer](#reject-offer-from-buyer)

- [Reject offer from owner](#reject-offer-from-owner)

- [Get all content](#get-all-content)

The following is a description of the API-methods:


## Create new account

* **URL:** `/api/accounts`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

    `[json]`

    **Optional:**

    `phone`

    All other fields are **required**.

```bash
    {
        "public_key": [string],
        "message": {
            "email": [string],
            "device_id": [string],
            "phone": [string],
            "timestamp": [string]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

    New account data with:

    User data:

    `public_key` 

    `email` 

    `device_id`

    `news_count` - number of news about offers to buy content (0 by default)

    `href` - link to user account

    `balance` - user balance (0 by default)

    `address` - user identifier (public key in hash format)

    System data:

    `id`

    `count`

    `level`

```bash
    {
        "public_key": [string], 
        "email": [string], 
        "device_id": [string], 
        "count": [int], 
        "level": [int], 
        "news_count": [int], 
        "id": [int], 
        "href": [string], 
        "balance": [float], 
        "address": [string]
    }
```


## Get account data

* **URL:** `/api/accounts/[public_key]`

* **Method:** `GET`

* **URL params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string]
        },
        "signature": [string]
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        "public_key": [string], 
        "email": [string], 
        "device_id": [string], 
        "phone": [string], 
        "count": [int], 
        "level": [int], 
        "news_count": [int], 
        "id": [int], 
        "balance": [float], 
    }
```


## Get last news for the account

* **URL:** `/api/accounts/[public_key]/news`

* **Method:** `GET`

* **URL params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string]
        },
        "signature": [string]
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

    When user send offer to buy content `event_type` is 'made offer'.

    `access_string` is equal to `buyer_pubkey`

```bash
    [
        {
            'event_type': [string], 
            'buyer_addr': [string], 
            'cid': [int], 
            'access_string': [string], 
            'buyer_pubkey': [string], 
            'account_id': [integer]
        }
    ]
```

* **Description**

    News about actions with user content.


## Get content from the blockchain

* **URL:** `/api/blockchain/[public_key]/content`

* **Method:** `GET`

* **URL params**

    `[json]`

    `hash=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        'cid': '24', 
        'data': 'wqsdsd', 
        'owner': '9df6a9ad7ac301098640a1b3a4968c2985ce7afc'
    }
```

## Post content to the blockchain

* **URL:** `/api/blockchain/[public_key]/content`

* **Method:** `POST`

* **URL params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cus": [string],
            "price": [string],
            "description": [string]
        },
        "signature": [string]
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

    `txid` - transaction id

    `sender` - user address

    `cus` - content

    `addr` - user address

    `owner_hex_addr` - hex of user address

```bash
    {
        "result": {
            "txid": [string], 
            "sender": [string], 
            "hash160": [string]
        }
        "hash": [string],  
        "cus": [string], 
        "addr": [string], 
        'owner_hex_addr": [string]
    }
```

* **Description**

    Post data to blockchain via transaction. When transaction will be approved (around 5-10 minutes) user can receive cid (Content-ID).


## Get description of content by cid

* **URL:** `/api/blockchain/[cid]/description`

* **Method:** `GET`

* **URL params**

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


## Set description of content for cid

* **URL:** `/api/blockchain/[cid]/description`

* **Method:** `POST`

* **URL params**

    `cid=[string]`

* **Body params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [string],
            "description": [string]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        'result': {
            'txid': [string], 
            'sender': [string], 
            'hash160': [string]
        }, 
        'cid': [string], 
        'descr': [string], 
        'addr': [string]
    }
``` 


## Get content price

* **URL:** `/api/blockchain/[cid]/price`

* **Method:** `GET`

* **URL params**

    `cid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        'price': [float]
    }
```


## Set content price

* **URL:** `/api/blockchain/[cid]/price`

* **Method:** `POST`

* **URL params**

    'cid=[string]'

* **Body params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [string],
            "price": [float]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        'result': {
            'txid': [string], 
            'sender': [string], 
            'hash160': [string]
        }, 
        'cid': [string], 
        'price': [float]
    }
```


## Make offer for buying the content

* **URL:** `/api/blockchain/[public_key]/offer`

* **Method:** `POST`

* **URL params**

    'public_key=[string]'

* **Body params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [string],
            "buyer_access_string": [string]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        'result': {
            'txid': [string], 
            'sender': [string], 
            'hash160': [string]
        }, 'cid': [string], 
        'buyer_addr': [string], 
        'buyer_access_string': [string]
    }
```


## Accept offer

* **URL:** `/api/blockchain/[public_key]/deal`

* **Method:** `POST`

* **URL params**

    'public_key=[string]'

* **Body params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [string],
            "buyer_access_string": [string],
            "buyer_pubkey": [string]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        'result': {
            'txid': [string], 
            'sender': [string], 
            'hash160': [string]
        }, 
        'cid': [string], 
        'buyer_addr': [string], 
        'access_string': [string], 
        'content_owner': [string], 
        'contract_owner_hex': [string], 
        'new_owner': [string], 
        'prev_owner': [string]
    }
```

* **Description**

    Accept offer to buy content


## Reject offer from buyer

* **URL:** `/api/blockchain/[public_key]/offer`

* **Method:** `PUT`

* **URL params**

    'public_key=[string]'

* **Body params**

    `[json]`

    `buyer_addr` is address of current user (he sent "make offer" to buy content before).

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "offer_id": {
                "cid": [string],
                "buyer_addr": [string]
            }
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        'result': {
            'txid': [string], 
            'sender': [string], 
            'hash160': [string]
        }, 
        'cid': [string], 
        'buyer_addr': [string]
    }
```

* **Description**

    Reject offer to buy content from buyer


## Reject offer from owner

* **URL:** `/api/blockchain/[public_key]/offer`

* **Method:** `PUT`

* **URL params**

    'public_key=[string]'

* **Body params**

    `[json]`

    `buyer_addr` is address of user who sent "make offer" request for buying content.

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "offer_id": {
                "cid": [string],
                "buyer_addr": [string]
            }
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        'result': {
            'txid': [string]', 
            'sender': [string], 
            'hash160': [string]
        }, 
        'cid': [string], 
        'buyer_addr': [string]
    }
```

* **Description**

    Reject offer to buy content from content owner


## Get all content

* **URL:** `/api/blockchain/content`

* **Method:** `GET`

* **URL params**

    None

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    [
        {
            'cid': [string], 
            'description': [string], 
            'price': [float], 
            'owner': [string], 
            'owneraddr': [string]
        },
        ...
    ]
```

* **Description**

    Get all content that present in the system
