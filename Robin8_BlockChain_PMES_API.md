# Profile Management EcoSystem API

The API uses the REST API standard.

The host you could find here: http://pdms.robin8.io.

Commonly integer numbers storing in the blockchains.
If you want to store float number in the blockchain, you should multiply it on some constant (for instance, `10^8` for QTUM).
Therefore, variables `amount`, `balance`, `offer_price`, `price`, `buyer_price` and `seller_price` represented as `x * 10^8`. Where `x` could be `float`.

Variable `timestamp` has the following format `%Y%m%d%H%M`. For instance, timestamp `201806081300` means 2018 June 8 13:00.

For checking status of the transaction in the QTUM blockchain use the following site https://testnet.qtum.org.

Your data is written to the blockchain when the status of the transaction changes from `Unconfirmed` to `Success`.

The API-methods:

- [Create new account](#create-new-account)

- [Get account data](#get-account-data)

- [Get all news for the account](#get-all-news-for-the-account)

- [Post profile to the blockchain](#post-profile-to-the-blockchain)

- [Get profile from the blockchain by cid](#get-profile-from-the-blockchain-by-cid)

- [Set description of profile for cid](#set-description-of-profile-for-cid)

- [Set profiles price](#set-profiles-price)

- [Make a profiles write access offer for owner](#make-a-profiles-write-access-offer-for-owner)

- [Make a profiles read access offer for owner](#make-a-profiles-read-access-offer-for-owner)

- [Accept buyers offer](#accept-buyers-offer)

- [Reject the read access offer by either buyer or seller](#reject-the-write-access-offer-by-either-buyer-or-seller)

- [Reject the read access offer by either buyer or seller](#reject-the-read-access-offer-by-either-buyer-or-seller)

- [Get all PMES profiles from the blockchain](#get-all-pmes-profiles-from-the-blockchain)

- [Get all profiles which posted user](#get-all-profiles-which-posted-user)

- [Get all offers which made user](#get-all-offers-which-made-user)

- [Get all offers by cid](#get-all-offers-by-cid)

- [Get all purchased read access profiles](#get-all-purchased-read-access-profiles)

- [Make review for purchased profile](#make-review-for-purchased-profile)

- [Get all profiles reviews](#get-all-profiles-reviews)

- [Withdraw PUT tokens](#withdraw-put-tokens)

- [Bulk operations](#bulk_operations)

- [Standardization of an error messages](#standardization-of-an-error-messages)


The following is a description of the API-methods:


## Create new account

* **URL:** `/api/accounts`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

    `[json]`

    **Optional:**

    `email` and `phone`

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

    There are the following user's balances present in the user's wallets: 

    - `amount` - an active amount of user's balance.

    - `deposit` - a frozen amount. When a user posted an offer to buy some content with price is 100 tokens, these tokens will be frozen and displays as "deposit" field.

    - `unconfirmed` - is the number of coins/tokens that is not confirmed in the blockchain yet. When transaction will be confirmed, this number of coins/tokens will be shown in the "amount" field.

    Therefore, when a buyer pays for buying profile from the seller the following steps happen:

    1) buyer sends tokens to the seller and this tokens will become frozen and will be shown in the `deposit` field

    2) seller receive tokens and they will be shown in the `unconfirmed` field until transaction will be confirmed in the blockchain

    `balance` represented as `real_user_balance * 10^8`. Where `real_user_balance` could be `float`.

    After successful account creation user receives the response with the following structure:

```bash
    {
        "count": [integer],         # number of user's wallets
        "device_id": [string],
        "email": [string],
        "href": [string],           # link to the user account
        "level": [integer],         # user account level (2 - when balance is zero (by default), 3 - when balance is not null)
        "public_key": [string],
        "news_count": [integer],    # number of news about offers to buy profile (0 by default)
        "id": [integer],            # identifier of the user account
        "wallets": [string],        # list of dicts with user's wallets addresses
            "address": [string],                # wallet address to which user could refill coins/tokens
            "amount": 0 [integer],              # an active amount of coins/tokens
            "deposit": 0 [integer],             # a frozen amount of coins/tokens
            "unconfirmed": 0 [integer],         # is the number of coins/tokens that is not confirmed in the blockchain yet
            "coinid": [string]                  # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
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
        "count": [integer],         # number of user's wallets
        "device_id": [string],
        "email": [string],
        "href": [string],           # link to user account
        "level": [integer],         # user account level (2 - when balance is zero ( by default), 3 - when balance is not null)
        "public_key": [string],
        "news_count": [integer],    # number of news about offers to buy profile (0 by default)
        "id": [integer],            # user's identifier
        "wallets": [string],        # list of dicts with user's wallets addresses
            "address": [string],                # wallet address to which user could refill coins/tokens
            "amount": 0 [integer],              # an active amount of coins/tokens
            "deposit": 0 [integer],             # a frozen amount of coins/tokens
            "unconfirmed": 0 [integer],         # is the number of coins/tokens that is not confirmed in the blockchain yet
            "coinid": [string]                  # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
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

    When the user sends an offer to buy profile `event_type` is `made offer`.

    `buyer_price` and `seller_price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        {
            "event_type": [string],     # type of news
            "access_string": [string],  # now it is user's public key
            "cid": [integer],           # profile identifier 
            "buyer_address": [string],  # buyer address
            "buyer_pubkey": [string],   # buyer public key
            "buyer_price": [integer],   # proposed buyer price * 10^8
            "seller_price": [integer],  # profiles price * 10^8
            "coinid": [string]          # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "offer_type": [string]      # offers type
        }
    ]
```

* **Description**

    News about actions with user profile.




## Post profile to the blockchain

* **URL:** `/api/blockchain/[public_key]/[coinid]/profile`

* **Method:** `POST`

* **URL params**

    `public_key=[string]`

    `coinid=[string]`

    `price` represented as `real_price * 10^8`. Where `real_price` (price of profile) could be `float`.

* **Body params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cus": [string],               # profile encrypted with private key
            "read_access": [integer],      # profile read access price * 10^8
            "write_access": [integer],     # profile write access price * 10^8
            "description": [string]        # profile description
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {

        "owneraddr": [string],           # owners address
        "description": [string],         # profiles description
        "read_price": [integer],         # read access price
        "write_read": [integer]        # write access price
    }
```


## Get profile from the blockchain by cid

* **URL:** `/api/blockchain/[cid]/[coinid]/profile`

* **Method:** `GET`

* **URL params**

    `cid=[string]`

    `coinid=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    {   
        "cid": [integer],                  # profile identifier
        "coinid": [string],                # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
        "description": [string],           # profile description
        "owner": [string],                 # owner public key
        "owneraddr": [string],             # owner address
        "read_access": [integer],          # profiles read access price * 10^8
        "write_access": [integer],         # profiles write access price * 10^8
        "content": [string],               # profile
        "seller_access_string": [string],  # seller access string
        "seller_pubkey": [string],         # seller public key
        "access_type": [string]            # access type of profile

    }
```

* **Description**

    Return content from the blockchain by content id


## Set description of profile for cid

**in progress**

* **URL:** `/api/blockchain/[cid]/description`

* **Method:** `PUT`

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
            "description": [string],
            "coinid": [string]
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "cid": [integer],         # profiles cid 
        "description": [string],  # profiles new description
        "owneraddr": [string],    # owner address
        "coinid": [string]        # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
    }
``` 


## Set profiles price

**in progress**

* **URL:** `/api/blockchain/[cid]/price`

* **Method:** `PUT`

* **URL params**

    `cid=[string]`

* **Body params**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [integer],
            "price": [integer],			# price * 10^8
            "coinid": [string] 			# type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "access_type": [string] (read_access, write_access)
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "cid": [integer],                           # profiles cid 
        "write_access" or "read_access": [integer]  # new profiles write access or read access price
        "coinid": [string]                          # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
    }
```


## Make a profiles write access offer for owner

* **URL:** `/api/blockchain/[public_key]/write-access-offer`

* **Method:** `POST`

* **URL params**

    `public_key=[string]`

* **Body params**

    `[json]`

```bash
    {
        "message": {
            "timestamp": [string],
            "cid": [integer],                   # profiles identifier
            "coinid": [string],                 # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "price": [integer],                 # write access price (optional, sellers price by default)
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
        "cid": [integer],                   # profile identifier
        "buyer_address": [string],          # buyer address
        "buyer_access_string": [string],    # now it is buyer's public key
        "offer_price": [integer],           # price of profile * 10^8
        "offer_type": [string]              # offers type (write access)
    }
```

## Make a profiles read access offer for owner

* **URL:** `/api/blockchain/[public_key]/read-access-offer`

* **Method:** `POST`

* **URL params**

    `public_key=[string]`

* **Body params**

    `[json]`

```bash
    {
        "message": {
            "timestamp": [string],
            "cid": [integer],                   # profiles identifier
            "coinid": [string],                 # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "price": [integer],                 # read access price (optional, sellers price by default)
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
        "cid": [integer],                   # profile identifier
        "buyer_address": [string],          # buyer address
        "buyer_access_string": [string],    # now it is buyer's public key
        "offer_price": [integer],           # price of profile * 10^8
        "offer_type": [string]              # offers type (read access)
    }
```


## Accept buyers offer

* **URL:** `/api/blockchain/[public_key]/deal`

* **Method:** `POST`

* **URL params**

    `public_key=[string]`

* **Body params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "cid": [integer],                   # profile identifier
            "buyer_access_string": [string],    # now it is user's public key
            "buyer_pubkey": [string],           # buyer public key
            "seller_access_string": [string],
            "access_type": [string],            # write access or read access
            "coinid": [string]                  # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
        },
        "signature": [string]
    }
```

* **Sample response**

    `[json]`

```bash
    {
        "cid": [integer],               # profile identifier
        "access_string": [string],      # now it is user's public key
        "new_owner": [string],          # address of the new owner
        "prev_owner": [string]          # address of the previous owner
    }
```





## Reject the write access offer by either buyer or seller

* **URL:** `/api/blockchain/[public_key]/write-access-offer`

* **Method:** `PUT`

* **URL params**

    `public_key=[string]`

* **Body params**

    `[json]`

    `buyer_address` is address of user who sent "make offer" request for buying profile.

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "offer_id": {
                "cid": [integer],           # profile identifier
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
        "cid": [integer],           # profile identifier
        "buyer_address": [string]   # buyer address
    }
```

## Reject the read access offer by either buyer or seller

* **URL:** `/api/blockchain/[public_key]/read-access-offer`

* **Method:** `PUT`

* **URL params**

    `public_key=[string]`

* **Body params**

    `[json]`

    `buyer_address` is address of user who sent "make offer" request for buying profile.

```bash
    {
        "public_key": [string],
        "message": {
            "timestamp": [string],
            "offer_id": {
                "cid": [integer],           # profile identifier
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
        "cid": [integer],           # profile identifier
        "buyer_address": [string]   # buyer address
    }
```


## Get all PMES profiles from the blockchain

* **URL:** `/api/blockchain/profile?page=`

* **Method:** `GET`

* **URL params**


    "page": [integer]

* **Body params**

    None

* **Sample response**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    {"profiles": [array]                     # array with profiles
        [
            {
                "cid": [integer],            # profile identifier
                "coinid": [string],          # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
                "description": [string],     # profile description
                "owneraddr": [string],       # owner address
                "read_access": [integer],    # profile read access price * 10^8
                "write_access": [integer],   # profile write access price * 10^8
                "txid": [string]             # transaction status reference
            },
        ...
        ],
    "pages":[integer]                        # number of used pages for pagination 
    }
```


## Get all profiles which posted user

* **URL:** `/api/accounts/[public_key]/profiles?page=`

* **Method:** `GET`

* **URL params**

    "page": [integer]

* **Body params**

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

* **Sample response**

    `[json]`

    `price` represented as `real_price * 10^8`. Where `real_price` could be `float`.

```bash
    [
        profiles: [array]                    # array with profiles
            [
                {
                    "cid": [integer],            # profile identifier
                    "coinid": [string]           # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
                    "description": [string],     # profile description
                    "owneraddr": [string],       # owner address
                    "read_access": [integer],    # profile read access price * 10^8
                    "write_access": [integer],   # profile write access price * 10^8
                    "txid": [string]             # transaction status reference

                }
            ]
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
            "buyer_access_string": [string],
            "buyer_address": [string],          # buyers address
            "cid": [integer],                   # profiles identifier
            "price": [integer],                 # offers price
            "seller_access_string": [integer],  # profile price * 10^8
            "type": [string],                   # offers type
            "coinid": [string],                 # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "status": [integer],                # offer status
            "seller_public_key": [string]       # seller public key
        },
        ...
    ]
```

* **Description**

    Get all offers which made the user for buying access or rights of profiles


## Get all offers by cid

* **URL:** `/api/accounts/[public_key]/input-offers`

* **Method:** `GET`

* **URL params**

    `[json]`

```bash
    {
        "public_key": [string],
        "message": {
            "cid": [integer],
            "timestamp": [string],
            "coinid": [string]		# type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
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
            "buyer_access_string": [string],
            "buyer_address": [string],          # buyers address
            "cid": [integer],                   # profiles identifier
            "price": [integer],                 # offers price
            "seller_access_string": [integer],  # content price * 10^8
            "type": [string],                   # offers type
            "coinid": [string],                 # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "status": [integer],                # offer status
            "seller_public_key": [string]       # sellers public key
        },
        ...
    ]
```

## Get all purchased read access profiles

* **URL:** `/api/accounts/[public_key]/deals`

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
            "cid": [integer],            # profile identifier
            "coinid": [string]           # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
            "description": [string],     # profile description
            "owneraddr": [string],       # owner address
            "read_access": [integer],    # profile read access price * 10^8
            "write_access": [integer],   # profile write access price * 10^8
            "txid": [string],            # transaction status reference

        },

    ]
```


## Make review for purchased profile

* **URL:** `/api/accounts/[public_key]/review`

* **Method:** `POST`

* **URL params**

    None


* **Body params**

```bash
        {
            "public_key": [string],
            "message": {
                "cid": [integer],       # profile identifier
                "timestamp": [string],
                "coinid": [string],     # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
                "review": [string],     # review
                "rating": [integer]     # profiles rating in range from 1 to 5
            },
            "signature": [string]
        }
```

* **Sample response**

    `[json]`

```bash
    [
         {   
            "review": [string],     # review
            "rating": [integer]     # profiles rating in range from 1 to 5
            "cid": [integer]        # profiles identifier
        },
        ...
    ]
```

## Get all profiles reviews

* **URL:** `/api/accounts/[cid]/[coinid]/reviews`

* **Method:** `GET`

* **URL params**

    `cid=[string]` - profile identifier

    `coinid=[string]` - type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)

* **Body params**

    None
    

* **Sample response**

    `[json]`

```bash
    [
         {   
            "review": [string],               # review
            "rating": [integer]               # profiles rating in range from 1 to 5
            "buyer_address": [integer]        # buyers address
            "confirmed": [integer]            # 1 by default
        },
        ...
    ]
```


##Withdraw PUT tokens

* **URL:** `/api/accounts/withdraw`

* **Method:** `POST`

* **URL params**

    None


* **Body params**
    
    Now work for the PUT tokens only.

```bash
        {
            "public_key": [string],
            "message": {
                "timestamp": [string],
                "coinid": [string],         # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
                "amount": [string],         # amount of tokens that user send to the "address"
                "address": [string],        # address to which user send the tokens
                "recvWindow": [integer]     # signature of the message timeout expired after this timing. For instance, in 5000 milliseconds
            },
            "signature": [string]
        }
```

* **Sample response**

    `[json]`

    `message` and `signature` is repeated from the user request respectively. The user could check the status of the transaction by viewing it by the `txid`.

```bash
        {
            "public_key": [string],
            "message": {
                "timestamp": [string],
                "coinid": [string],         # type of the blockchain (ETH - Ethereum blockchain, QTUM - QTUM blockchain)
                "amount": [string],         # amount of tokens that user send to the "address"
                "address": [string],        # address to which user send the tokens
                "recvWindow": [integer]     # signature of the message timeout expired after this timing. For instance, in 5000 milliseconds
            },
            "signature": [string],
            "txid": [string]                # transaction identifier
        }
```


##Bulk operations

* **URL:** `/api/bulk`

* **Method:** `POST`

* **URL params**

    None


* **Body params**
    
    Now work for the PUT tokens for sending tokens only.

    Full JSON format of the bulk operation is present [here](bulk_operations_json_format_description.js).

    `txid` field shouldn't be filled by user, it will be filled by the PMES in the response.

    Part of bulk operation is present bellow:

```bash
var test = {
    "message": {                            # signed json
        "send": [{
            "message":{
                    "input": "address1",    # sender addresses
                    "output": "address2",   # receiver addresses
                    "amount": "value",
                    "coinid": "coinid",     # blockchain type
                    "txid": null,           # txid will filled with response
                    "error": null,
                    "response": null
                },
                "signature": "signature",   # users signature
                "public_key": "public_key", # users public key
            }
        ],
        ...
    },
    "decimal": 8,
    "signature": "signature",
    "public_key": "public key",
    "callbackURL": "some_url" // PMES backend reply send to this endpoint
}
```

* **Sample response**

    `[json]`

    In the response, user receives filled JSON format of the bulk operation with server signature.


## Standardization of an error messages 

A standard error answer from the server has the following structure:

```bash
{
    "error": [integer], 
    "reason": [string]}
```

Where `error` contains an error code, while `reason` contains error description.
