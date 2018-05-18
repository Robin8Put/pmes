# Drivers has next functionality

- [Read data from database](#read-data-from-database)
- [Insert data to database](#insert-data-to-database)
- [Update fields values in database](#update-fields-values-in-database)
- [Find all entries with given search key in database](#find-all-entries-with-given-search-key-in-database)
- [Delete entry from database table](#delete-entry-from-database-table)


## Read data from database

* **Method:** `read`

* **Params**

    `*id` - ids of entries

* **Return**

    list of results if success or string with error code and explanation

* **Usage example**

```bash
    read(*id) => [(result), (result)] (if success)
    read(*id) => [] (if missed)
    read() => {"error":400, "reason":"Missed required fields"}
```

## Insert data to database

* **Method:** `insert`

* **Params**

    `**kwargs` - field names and values

* **Return**

    Return success or error based on posibility to pass arbitrary amount of parameters.

* **Usage example**

```bash
    insert(**kwargs) => {1: 'Success'}
    insert(**kwargs) => {3: 'Error text'}
```

## Update fields values in database

* **Method:** `update`

* **Params**

    `*id` - id of sigle entry

    `**kwargs` - field names and values

* **Return**

    Return success or error based on posibility to update parameters.

* **Usage example**

```bash
    update(id, **kwargs) => {3: 'Created/Updated'} (if success)
    update(id, **kwargs) => {5: 'Error'} (if error)
```

## Find all entries with given search key in database

* **Method:** `find`

* **Params**

    `key` - named parameter

    `*values` - arbitrary values

* **Return**

    Return success or error based on posibility to find entries.

* **Usage example**

```bash
    find(key, *values) => [id, id, id, id] (if exist)
    find(key, *values) => [] (if does not exist)
    find() => {5: "Missed required fields"}
```

## Delete entry from database table

* **Method:** `delete`

* **Params**

    `id` - id of entry that will be deleted

* **Return**

    Return success or error based on posibility to find entries.

* **Usage example**

```bash
    delete(id) => {0: True} (if exists)
    delete(id) => {5: 'Error'} (if does not exist)
    delete() => {5: 'Missed required fields'}
```
