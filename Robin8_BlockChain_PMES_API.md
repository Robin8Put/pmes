# Robin8 BlockChain Profile Management EcoSystem

This API provides access to information of Profile Management EcoSystem (PMES).

The API uses the REST API standard.

The host is here: http://pdms.robin8.io.

`balance`, `price`, `buyer_price` and `seller_price` represented as `real_entity * 10^8`. Where `real_entity` could be `float`.

The API-methods:

- [Create new account](#create-new-account)

- [Get account data](#get-account-data)

- [Get all news for the account](#get-all-news-for-the-account)

- [Increment balance](#increment-balance)

- [Post content to the blockchain](#post-content-to-the-blockchain)

- [Get content from the blockchain by cid](#get-content-from-the-blockchain-by-cid)

- [Set description of content for cid](#set-description-of-content-for-cid)

- [Set content price](#set-content-price)

- [Make offer for buying the content](#make-offer-for-buying-the-content)

- [Make offer for buying the content with proposed price](#make-offer-for-buying-the-content-with-proposed-price)

- [Accept offer](#accept-offer)

- [Reject offer from buyer](#reject-offer-from-buyer)

- [Reject offer from owner](#reject-offer-from-owner)

- [Get all content](#get-all-content)

- [Get all content which post user](#get-all-content-which-post-user)

- [Get all offers which made user](#get-all-offers-which-made-user)

- [Get all offers received for content by cid](#get-all-offers-received-for-content-by-cid)

The following is a description of the API-methods:


## Create new account

* **URL:** `/api/accounts`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

    `[json]`

    **Optional:**

    `phone` and `email`

    **Required:**

    `device_id`

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

    If such account already exists user receives a `Unique violation error`.

    `balance` represented as `real_user_balance * 10^8`. Where `real_user_balance` could be `float`.

    After successful account creation user receives the response with following structure:

```bash
    {
        "public_key": [string],
        "email": [string],
        "phone": [string],
        "device_id": [string],
        "count": [int],         # number of wallets
        "level": [int],         # user account level (2 - when balance is zero (by default), 3 - when balance is not null)
        "news_count": [int],    # number of news about offers to buy content (0 by default)
        "id": [int],            # user's identifier
        "href": [string],       # link to user account
        "balance": [integer],   # user balance (0 by default)
        "address": [string]     # user identifier (public key in hash format)
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
        "address": [string],    # user's wallet address
        "public_key": [string], 
        "email": [string], 
        "phone": [string], 
        "device_id": [string], 
        "phone": [string], 
        "count": [int], 
        "level": [int], 
        "news_count": [int], 
        "id": [int], 
        "balance": [float], 
    }
```


## Get all news for the account

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

    `access_string` is equal to `buyer_pubkey` now.

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


## Increment balance

**temporary function**

* **URL:** `/api/accounts/[user_id]/balance`

* **Method:** `POST`

* **URL params**

    `[json]`

```bash
    {
        "amount": [int]
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

    When user send offer to buy content `event_type` is 'made offer'.

    `access_string` is equal to `buyer_pubkey` now.

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

    Increment user's balance with test coins.


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


## Get content from the blockchain by cid

* **URL:** `/api/blockchain/[cid]/content`

* **Method:** `GET`

* **URL params**

    `cid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {   
        'account_id': [int],
        'cid': [int],
        'content': [string],
        'description': [string],
        'owner': [string],
        'price': [int],
        'txid': [string]
    }
```

* **Description**

    Return content from the blockchain by content id


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

## Make offer for buying the content with proposed price

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
            "buyer_access_string": [string],
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


## Get all content which post user

* **URL:** `/api/accounts/[public_key]/contents`

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

## Get all offers which made user

* **URL:** `/api/accounts/[public_key]/output-offers`

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
    [
        {
            'cid': [string],
            'buyer_price': [float],
            'seller_price': [float],
            'buyer_addr': [string], 
            'buyer_pubkey': [string]
        },
        ...
    ]
```

* **Description**

    Get all offers which made user to buy access or rights of contents


## Get all offers received for content by cid

* **URL:** `/api/accounts/[public_key]/input-offers`

* **Method:** `GET`

* **URL params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "cid": [string]
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
    [
        {
            'cid': [string],
            'buyer_price': [float],
            'seller_price': [float],
            'buyer_addr': [string], 
            'buyer_pubkey': [string]
        },
        ...
    ]
```

## Error message

Standard error answer from the server has next structure:

```bash
{
    'error': [int], 
    'reason': [string]}
```

Where `error` contains error code, while `reason` contains error description.
