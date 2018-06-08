# Robin8 BlockChain Profile Management EcoSystem

This API provides access to information of Profile Management EcoSystem (PMES).

The API uses the REST API standard.

The host is here: http://pdms.robin8.io.

`amount`, `balance`, `offer_price`, `price`, `buyer_price` and `seller_price` represented as `x * 10^8`. Where `x` could be `float`.

`timestamp` has following format `%Y%m%d%H%M`. For instance, `201806081300` means 2018 June 8 13:00.

For checking status of transaction in the QTUM blockchain you could use the site https://testnet.qtum.org.
When the status of transaction changes from `Unconfirmed` to `Success` this means that your data was written to the blockchain.

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
        "address": [string],     # user's wallet address
        "public_key": [string],
        "email": [string],
        "phone": [string],
        "device_id": [string],
        "count": [integer],         # number of user's wallets
        "level": [integer],         # user account level (2 - when balance is zero (by default), 3 - when balance is not null)
        "news_count": [integer],    # number of news about offers to buy content (0 by default)
        "id": [integer],            # user's identifier
        "href": [string],       # link to user account
        "balance": [integer],   # user balance (0 by default) * 10^8
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

    `balance` represented as `real_user_balance * 10^8`. Where `real_user_balance` could be `float`.

```bash
    {
        "address": [string],    # user's wallet address
        "public_key": [string], 
        "email": [string], 
        "phone": [string], 
        "device_id": [string], 
        "phone": [string], 
        "count": [integer],         # number of user's wallets
        "level": [integer],         # user account level (2 - when balance is zero (by default), 3 - when balance is not null)
        "news_count": [integer],    # number of news about offers to buy content (0 by default
        "id": [integer],            # user's identifier
        "balance": [integer],   # user balance (0 by default) * 10^8
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

    `buyer_price` and `seller_price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        {
            "event_type": [string],     # 
            "access_string": [string],  # now it is user's public key
            "cid": [integer],           # content identifier 
            "buyer_address": [string],  # buyer address
            "buyer_pubkey": [string],   # buyer public key
            "buyer_price": [integer],   # proposed buyer price * 10^8
            "seller_price": [integer],  # content price * 10^8
            "account_id": [integer]     # account identifier
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

    `amount` represented as `real_amount * 10^8`. Where `real_amount` (amount on which you want to increment user's balance) could be `float`.

```bash
    {
        "amount": [integer]
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

    `amount` represented as `real_amount * 10^8`. Where `real_amount` could be `float`.

```bash
    {
        "address": [sting],     # wallet address
        "coinid": [sting],      # type of coin (for instance, "qtum")
        "amount": [integer],    # updated amout of coins on the user's balance * 10^8
        "uid": [integer]        # user's identifier
    }
```

* **Description**

    Increment user's balance with test coins.


## Post content to the blockchain

* **URL:** `/api/blockchain/[public_key]/content`

* **Method:** `POST`

* **URL params**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` (price of content) could be `float`.

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cus": [string],        # content encrypted with private key
            "price": [integer],     # content price * 10^8
            "description": [string] # content description
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
        "result": {
            "txid": [string],       # transaction id
            "sender": [string],     # user address
            "hash160": [string]     # transaction hash
        }
        "hash": [string],           # transaction hash which identify posted content in the blockchain
        "cus": [string],            # content
        "addr": [string],           # user's address
        'owner_hex_addr": [string]  # hex of user address
    }
```

* **Description**

    Post data to blockchain via transaction. When transaction will be approved (around 5-10 minutes) user could see posted content in the result of following command [Get all content which post user](#get-all-content-which-post-user).


## Get content from the blockchain by cid

* **URL:** `/api/blockchain/[cid]/content`

* **Method:** `GET`

* **URL params**

    `cid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    {   
        "account_id": [integer],    # account identifier
        "cid": [integer],           # content identifier
        "content": [string],        # encrypted content
        "description": [string],    # content description
        "owner": [string],          # owner public key
        "price": [integer],         # content price * 10^8
        "txid": [string]            # transaction identifier
    }
```

* **Description**

    Return content from the blockchain by content id


## Set description of content for cid

**in progress**

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
            "cid": [integer],
            "description": [string]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result": {
            "txid": [string], 
            "sender": [string], 
            "hash160": [string]
        }, 
        "cid": [integer], 
        "descr": [string], 
        "addr": [string]
    }
``` 


## Set content price

**in progress**

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
            "cid": [integer],
            "price": [integer]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result": {
            "txid": [string], 
            "sender": [string], 
            "hash160": [string]
        }, 
        "cid": [integer], 
        "price": [integer]
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
            "cid": [integer],                   # content identifier
            "buyer_access_string": [string]     # now it is user's public key
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

    `offer_price` represented as `real_offer_price * 10^8`. Where `real_offer_price` could be `float`.

```bash
    {
        "result": {
            "txid": [string],               # transaction id
            "sender": [string],             # user address
            "hash160": [string]             # transaction hash
        }, 
        "cid": [integer],                   # content identifier
        "buyer_address": [string],          # buyer address
        "buyer_access_string": [string],    # now it is buyer's public key
        "offer_price": [integer]            # price of content * 10^8
    }
```

## Make offer for buying the content with proposed price

* **URL:** `/api/blockchain/[public_key]/offer`

* **Method:** `POST`

* **URL params**

    'public_key=[string]'

* **Body params**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` (price proposed for buying contnet) could be `float`.

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [integer],                   # content identifier
            "buyer_access_string": [string],    # now it is user's public key
            "price": [integer]                  # proposed price for content * 10^8
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

    `offer_price` represented as `real_offer_price * 10^8`. Where `real_offer_price` could be `float`.

```bash
    {
        "result": {
            "txid": [string],               # transaction id
            "sender": [string],             # user address
            "hash160": [string]             # transaction hash
        },
        "cid": [integer],                   # content identifier
        "buyer_addr": [string],             # buyer address
        "buyer_access_string": [string],    # now it is user's public key
        "offer_price": [integer]            # price of content * 10^8
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
            "cid": [integer],                   # content identifier
            "buyer_access_string": [string],    # now it is user's public key
            "buyer_pubkey": [string]            # buyer public key
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result": {
            "txid": [string],           # transaction id
            "sender": [string],         # user address
            "hash160": [string]         # transaction hash
        }, 
        "cid": [integer],               # content identifier
        "buyer_address": [string],      # buyer address
        "access_string": [string],      # now it is user's public key
        "content_owner": [string],      # address of the content owner
        "contract_owner_hex": [string], # hex of the address of the content owner
        "new_owner": [string],          # address of the new owner
        "prev_owner": [string]          # address of the previous owner
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
                "cid": [integer],           # content identifier
                "buyer_address": [string]   # buyer address
            }
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result": {
            "txid": [string],       # transaction id
            "sender": [string],     # user address
            "hash160": [string]     # transaction hash
        }, 
        "cid": [integer],           # content identifier
        "buyer_address": [string]   # buyer address
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
                "cid": [integer],           # content identifier
                "buyer_address": [string]   # buyer address
            }
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "result": {
            "txid": [string]",      # transaction id
            "sender": [string],     # user address
            "hash160": [string]     # transaction hash
        }, 
        "cid": [integer],           # content identifier
        "buyer_address": [string]   # buyer address
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

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        {
            "cid": [integer],           # content identifier
            "content": [string],        # encrypted content
            "description": [string],    # content description
            "price": [integer],         # content price * 10^8
            "owner": [string],          # owner public key
        },
        ...
    ]
```

* **Description**

    Get all content that present in the blockchain


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
        "signature": [string]c.
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        {
            "cid": [integer],            # content identifier
            "content": [string],         # encrypted content
            "description": [string],     # content description
            "price": [integer],          # content price * 10^8
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

    `buyer_price` and `seller_price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        {
            "cid": [integer],           # content identifier
            "buyer_price": [integer],   # proposed buyer price * 10^8
            "seller_price": [integer],  # content price * 10^8
            "owner_addr": [string],     # content owner's address
            "owner_pubkey": [string]    # content owner's public key
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
            "cid": [integer]
            "timestamp": [string]
        },
        "signature": [string]
    }
```

* **Body params**

    None

* **Sample response**

    `[json]`

    `buyer_price` and `seller_price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        {
            "cid": [integer],           # content identifier
            "buyer_price": [integer],   # proposed buyer price * 10^8
            "seller_price": [integer],  # content price * 10^8
            "buyer_addr": [string],     # buyer's address
            "public_key": [string]      # buyer's public key
        },
        ...
    ]
```

## Error message standardization

Standard error answer from the server has next structure:

```bash
{
    "error": [integer], 
    "reason": [string]}
```

Where `error` contains error code, while `reason` contains error description.
