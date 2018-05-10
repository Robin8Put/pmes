# Robin8 BlockChain HISTORY API

This API provides access to information of Robin8 history module.

The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification).

API-methods:

- [Save logs about actions and history of transactions](#save-logs-about-actions-and-history-of-transactions)

- [Read logs](#read-logs)

- [Drop table](#drop-table)

The following is a description of the API-methods:

## Save logs about actions and history of transactions

* **Method:** `log`
  
* **Params**

    `module=[string]` - module name

    `table=[string]` - table name

    `event=[string]`

    `*args=[array]` - other parameters needed for logging to the table

* **Sample response**

```bash
    {
        "jsonrpc": "2.0", 
        "result": "3", 
        "id": 1
    } (200 OK)
```


## Read logs

* **Method:** `select`
  
* **Params**

    `table=[string]` - table name

    `query=[string]` - SQL query, alternative for WHERE section in SQL queries, example: 'WHERE id=1'

* **Sample response**

```bash
    {
        "jsonrpc": "2.0", 
        "result": "[(1, '123', 'transaction initiation', datetime.date(2018, 5, 8), datetime.datetime(2018, 5, 8, 14, 51, 24), ('awdaw',))]", 
        "id": 1
    } (200 OK)
```

## Drop table

* **Method:** `drop`
  
* **Params**

    `table=[string]` - table name

* **Sample response**

    None
