# Robin8 BlockChain BALANCE API

This API provides access to information of Robin8 balance module.

The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification).

API-methods:

- [Add wallet](#add-wallet)

- [Increment balance](#increment-balance)

- [Decrement balance](#decrement-balance)

- [Get balance](#get-balance)

The following is a description of the API-methods:

## Add wallet

* **Method:** `addaddr`
  
* **Params**
   
    `coin_id=[string]` - type of coins from list [“btc”, “eth”, “ltc”, "qtum"] where

    - btc – Bitcoin
    - eth – Ethereum
    - ltc – Litecoin
    - qtum –  Qtum
   
    `addr=[string]` - wallet address
   
    `uid=[string]` - user id
   
    `amount=[float]` - initial amount of coins

* **Sample response**

    None


## Increment balance

* **Method:** `incbalance`
  
* **Params**
   
    `addr=[string]` - wallet address
   
    `amount=[float]` - amount to which we will increment the balance

* **Sample response**

    None


**Decrement balance**
----

* **Method:** `decbalance`
  
* **Params**
   
    `addr=[string]` - wallet address
   
    `amount=[float]` - amount to which we will decrement the balance

* **Sample response**

    None


**Get balance**
----

* **Method:** `getbalance`
  
* **Params**
   
    `uid=[string]` - user id

* **Sample response**

    `[dictionary]` = `{[string]: [float]}`

    For example: `{addr1: balance1, addr2: balance2}`


* **Description**

    Return all wallets and amount of coins on them
