# Robin8 BlockChain AMS API

This API provides access to Account Management System (AMS) module.

The API uses the REST API standard.

API-methods:

- [Create account](#create-account)

- [Get account data](#get-account-data)

- [Get balance by public key](#get-balance-by-public-key)

The following is a description of the API-methods:


## Create account

* **URL:** `/api/accounts/`

* **Method:** `POST`

* **URL params**

    None

* **Body params**

    timestamp format: "year|month|day|hour|minute"

    example: "201805051836"

```bash
    {
        "public_key": "04e1f5bb5e6bb406e1a09353e1cab33023909849d13bcd44b920aacaba6404ce9eaa54ff55d9940840d1b740ddf9ffcddec64f752285274a76f2a87b12cf787c39", 
        "email": "email.com", 
        "device_id": "device_id", 
        "count": "1", 
        "level": "2", 
        "id": 7, 
        "href": "/api/accounts/04e1f5bb5e6bb406e1a09353e1cab33023909849d13bcd44b920aacaba6404ce9eaa54ff55d9940840d1b740ddf9ffcddec64f752285274a76f2a87b12cf787c39", 
        "balance": 0, 
        "address": "QhBfTdXZkvF3kKkD4T2YQt6NmQxKgKtuSo'
    }
```

* **Sample response**


## Get account data

* **URL:** `/api/accounts/public_key/?message=&signature=`

* **Method:** `GET`

* **URL params**

    `message=[string]`

    `signature=[string]`

* **Body params**

    None

* **Sample response**

    `[json]`

```bash
    {
        "public_key": "04cd5b82471a7628c28dee03c7f4efd5723a2e7e2f2ff4c7f832bbdd38d0aece4e7cffa9ab786d9085e336acf43b3bff072a5d4f6b937997498531ecd010a5ff55", 
        "email": "email.com", 
        "device_id": "device_id", 
        "count": "1", 
        "level": "2", 
        "id": 8, 
        "balance": {"QjWAS9ugnAGxLHL3J7hcwgK6QXrbNSAbmn": 0}}
```

## Get balance by public key

* **URL:** `/api/accounts/public_key/balance/`

* **Method:** `GET`

* **URL params**

    None

* **Body params**

    None

* **Sample response**

    [json]

```bash
    {
        "QXJPPYsBuvNxCjQx5RQ2F9PZyhoFgpLasT": [float]
    }
```
