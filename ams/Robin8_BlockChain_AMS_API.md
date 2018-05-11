# Robin8 BlockChain AMS API

This API provides access to Account Management System (AMS) module.

The API uses the REST API standard.

API-methods:

- [Add wallet](#add-wallet)

- [Increment balance](#increment-balance)

- [Decrement balance](#decrement-balance)

- [Get balance](#get-balance)

The following is a description of the API-methods:


## Create account

* **URL:** `/api/ams/`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

    timestamp format: "year|month|day|hour|minute"

    example: "201805051836"

```bash
    {
        “message”: {
            “email”: [string],
            “device_id”: [string],
            “timestamp”: [string]
        }
        “public_key”: [string],
        “signature”: [string]
    }
```

* **Sample response**


## Get account data

* **URL:** `/api/account/public_key/?message=&signature=`

* **Method:** `GET`

* **URL params**

    `message=[string]`

    `signature=[string]`

* **Body params**

    None

* **Sample response**


## Get balance by public key

* **URL:** `/api/balance/public_key/`

* **Method:** `GET`

* **URL params**

    None

* **Body params**

    None

* **Sample response**

    [float]
