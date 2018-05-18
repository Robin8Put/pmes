# Tornado components

- `rpc_client.py` --- contains `RPCClient` which represent custom jsonrpc client. It includes processing of connection errors also.
    - `request` --- make request to method by provided host address
    - `post` --- make post request to method by provided host address with provided parameters
    - `lastblockid` --- return last block id
    - `data_from_blockchain` --- get content from blockchain
    - `getownerbycid` --- get owner by CID (Content IDentifier)
    - `getcontentdescr` --- get content description
    - `postcontent` --- post content
    - `setdescrforcid` --- set description for CID
    - `last_access_string` --- get last access string
    - `changeowner` --- change content owner
    - `sellcontent` --- sell content
- `timestamp.py` --- convert data to `%Y%m%d%H%M` format. For example, `"201805101200"`
- `web.py` --- contains `ManagementSystemHandler` class which has sign-verify decorators for both http and rpc requests
- Storage RW module
    Read-Write drivers that provide same interface to work with Mongo DB and Postgre SQL.

    Functionality description is [here](db_drivers_functionality.md).

    - `mongo.py`
    - `psql.py`

