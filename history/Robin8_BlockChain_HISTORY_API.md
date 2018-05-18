# Robin8 BlockChain HISTORY API

This API provides access to information of Robin8 history module.

The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification).

API-methods:

- [Save logs about actions and history of transactions](#save-logs-about-actions-and-history-of-transactions)

- [Read logs](#read-logs)

- [Drop table](#drop-table)

The following is a description of the API-methods:

## Save logs about actions and history of transactions

* **Method:** `create_table`
  
* **Params**

    `table=[string]` - table name

    `fields={'field_name': [type(bits, sign), index]}` - fields in table

* **Sample request**

```bash
    {
        "jsonrpc": "2.0"
        "table": "table_name"
        "fields": {"id": ["int(32, signed)", "yes"], "field1": ["string", "no"], "field2": ["float(32)", "no"]}
    }
```

**Note.** For int type available bits are 8, 16, 32, 64, for float type only 32 and 64, float type is always signed

* **Sample response**

```bash
    {
        "jsonrpc": "2.0", 
        "result": "Table was successfully created", 
        "id": 1
    } (200 OK)
```

* **Method:** `insert`
  
* **Params**

    `table=[string]` - table name

    `fields={'field_name': value}` - fields in table with values

* **Sample request**

```bash
    {
        "jsonrpc": "2.0"
        "table": "table_name"
        "fields": {"id": "1241", "uid": 32, "coinid": "QTUM", "amount": 10.0}
    }
```

* **Sample response**

```bash
    {
        "jsonrpc": "2.0", 
        "result": "Data was successfully inserted into table", 
        "id": 1
    } (200 OK)
```

## Read logs

* **Method:** `select`
  
* **Params**

    `table=[string]` - table name

    `query=[string]` - SQL query, alternative for WHERE section in SQL queries, example: 'WHERE id=1'

    `fields=[string]` - fields to select

* **Sample request**

```bash
    {
        "jsonrpc": "2.0"
        "table": "table_name"
        "fields": "uid, amount"
    }
```

* **Sample response**

```bash
    {
        "jsonrpc": "2.0", 
        "result": "[{'uid': 1, 'amount': 5.0}, {'uid': 1, 'amount': 5.0}, {'uid': 1, 'amount': 5.0},{'uid': 1, 'amount': 5.0}"
        "id": 1
    } (200 OK)
```

## Drop table

* **Method:** `drop`
  
* **Params**

    `table=[string]` - table name

* **Sample response**

```bash
    {
        "jsonrpc": "2.0", 
        "result": "Table was successfully deleted", 
        "id": 1
    } (200 OK)
```