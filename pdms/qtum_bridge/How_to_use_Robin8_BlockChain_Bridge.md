How to use Robin8 BlockChain Bridge to access the information about Robin8's Smart Contract based on Qtum BlockChain.

In this document real host and port was replaced with ams_api_host_address:port.

Mock clients are placed in the [mock_clients](https://bitbucket.org/robin8_put/mock_clients).

Robin8 BlockChain Bridge log sample:

- Client makes registration and generates public and private keys.

```bash
>>> from client import Client
>>> c = Client()
>>> response = c.create('my device id', 'my email')
post request:  http://ams_api_host_address:port/api/accounts
public key:  e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326
device_id:  my device id
email:  my email
message:  create201804271843
signature:  a5c5496bc53feaf197225fbc16745453f29e1263adc3c2936b9f86fdffbebb4503fc1837c8b3f4c4eb55d87fc515cd85c4973fb53c0c3b5ae3440d70723ef6bb
>>> response
{'hyper': {'account': '/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326'}, 'status': 200, 'reason': 'Success', 'account': {'count': '1', 'level': '2', 'balance': 0, 'phone': None, 'address': 'QUBjTFUDuxTGuC97G57TGy7Md1XYTHM6L7', 'device_id': 'my device id', 'public_key': 'e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326', 'email': 'my email', 'id': 169}}
```

- Then uploads a file.

```bash
>>> response = c.upload_file('testfile', 'password')
file data:  b'User profile content\n\n'
hex_data:  557365722070726f66696c6520636f6e74656e740a0a
encrypted data:  pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=
post request: http://ams_api_host_address:port/api/accounts
public key: e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326
owneraddr: qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis
data: pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=
message: createDatapWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=201804271844
signature: 348e405479a57c93a65b7b26ba3d79fac11534c98e41131030bae8922b1db843a9f5a89ef91974c16bf85b9179d030abae392f36f1cff38a944ae73c223dea27
url: http://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326
>>> txid = response['result']['txid']
>>> txid
'6477f55b7175b67963605180cb49fb42d6c24fc9c5c7fc5e017d87580d4575f8'
>>> hash = response['hash']
>>> hash
'QmPmqcmwif3Kh5pJz9Tc2SFDGCdPtRdUZgUnbNkKGn9Xgs'
```

Bridge log:

```bash
INFO:jsonrpcserver.dispatcher.request:{"jsonrpc": "2.0", "method": "makecid","params":{"owneraddr": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis", "cus": "pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E="},"id": 1}
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": {"hash": "QmPmqcmwif3Kh5pJz9Tc2SFDGCdPtRdUZgUnbNkKGn9Xgs", "owner_hex_addr": "fdc1ae05c161833cdf135863e332126e15d7568c", "cus": "pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=", "owneraddr": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis", "result": {"sender": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis", "txid": "6477f55b7175b67963605180cb49fb42d6c24fc9c5c7fc5e017d87580d4575f8", "hash160": "fdc1ae05c161833cdf135863e332126e15d7568c"}, "addr": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis"}, "id": 1}
```

- After that user gets his data by received hash.

```bash
>>> result = c.get_data_by_hash(hash)
http://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326/?message=getData201804271900&signature=88d9a33db0e4c8c1e83a2b5a7b62e07cfa95b75962e41bbb92466857442df21df51beb94381c544560a3a7a772a30eb282f07d51eae2276185efc0253ebecf8e&hash=QmPmqcmwif3Kh5pJz9Tc2SFDGCdPtRdUZgUnbNkKGn9Xgs
>>> result['data']
'pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E='
>>> cid = result['cid']
>>> cid
'22'
```

Bridge log:

```bash
INFO:jsonrpcserver.dispatcher.request:{"id": 24, "method": "ipfscat", "jsonrpc": "2.0", "params": {"hash": "QmPmqcmwif3Kh5pJz9Tc2SFDGCdPtRdUZgUnbNkKGn9Xgs"}}
b'pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E='
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": "pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=", "id": 24}
{"id": 25, "method": "getcid", "jsonrpc": "2.0", "params": {"hash": "QmPmqcmwif3Kh5pJz9Tc2SFDGCdPtRdUZgUnbNkKGn9Xgs"}}
INFO:jsonrpcserver.dispatcher.request:{"id": 25, "method": "getcid", "jsonrpc": "2.0", "params": {"hash": "QmPmqcmwif3Kh5pJz9Tc2SFDGCdPtRdUZgUnbNkKGn9Xgs"}}
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": "22", "id": 25}
{"jsonrpc": "2.0", "method": "setdescrforcid","params":{"cid": "22", "descr": "Description for my profile data"},"id": 1}
```

- Also client can set data description.

```bash
>>> response = c.set_descr(cid, 'Description for my profile data')
http://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326/descr
post request:  http://ams_api_host_address:porthttp://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326/descr
public key:  e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326
cid:  22
descr:  Description for my profile data
message:  setDescrDescription for my profile data201804271902
signature:  a9e8f2e0bab56a1a63c4d32550184981b61a7f5dec928f0bf8f4d1504087f8b5451adb7d88593ebcae26e2e482deb3663aec70659b5d68e67b032fd5c1c86dc4
url:  http://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326/descr
>>> txid = response['result']['txid']
>>> txid
'b6a3a906a8826a962ae135809cbb076f7423e4ed912d814245c5abdd5a96f805'
```

Bridge log:

```bash
INFO:jsonrpcserver.dispatcher.request:{"jsonrpc": "2.0", "method": "setdescrforcid","params":{"cid": "22", "descr": "Description for my profile data"},"id": 1}
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": {"addr": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis", "descr": "Description for my profile data", "result": {"sender": "qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis", "txid": "b6a3a906a8826a962ae135809cbb076f7423e4ed912d814245c5abdd5a96f805", "hash160": "fdc1ae05c161833cdf135863e332126e15d7568c"}, "cid": "22"}, "id": 1}
```

- User can retrieve his description for his data by the following command:

```bash
>>> response = c.get_descr(cid)
http://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326/descr/?message=getDescr201804271905&signature=65ea982b27be55be10b27b5bb3b671bba20870de37a3c6e20b6b84e35fc5939631cc5a823a22887eb05f547587b1f194bed65ef9569a0f7325ac916131e7918b&cid=22
>>> response
{'descr': 'Description for my profile data'}
>>> descr = response['descr']
>>> descr
'Description for my profile data'
```

Bridge log:

```bash
INFO:jsonrpcserver.dispatcher.request:{"id": 26, "method": "descrbycid", "jsonrpc": "2.0", "params": {"cid": "22"}}
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": "Description for my profile data", "id": 26}
```

- Also user can decrypt downloaded data and write it to the file.

```bash
>>> c.download_file('downloaded', 'password', cid)
http://ams_api_host_address:port/api/accounts/e8e5b1009856e3ecd6e8fd93eef4454332675cb8237983fa6c8b35e50acb70490739fa886979d51bd57d3a93026166e3f014a655d23b0b924f90d73bb4d34326/?message=getData201804271906&signature=72c1d4fdf2f4d802a1bf5c65b6878ea93236ba63bedb5fa2274e3fcf6f35aaf60008d6ed32a1d27e20d33bab4b41d276182a40eab834af5aac7661e095d25397&cid=22
encrypted data:  pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=
decrypted_data:  557365722070726f66696c6520636f6e74656e740a0a
raw_data:  b'User profile content\n\n'
```

Bridge log:

```bash
INFO:jsonrpcserver.dispatcher.request:{"id": 27, "method": "readbycid", "jsonrpc": "2.0", "params": {"cid": "22"}}
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": "pWX3rZPhgwd/ksbzpyXMzlIwovf6DGwF/33NNIygmPhkrbOcDQm3oG3SZGPM7IBCW3u9FCkp2ptrCrzlVmo1DfQtB8ZcmM8JPMIO8q6rQ1E=", "id": 27}
```

- User can get last block id by using next code:

```bash

>>> response = Client.lastblockid()
http://ams_api_host_address:port/api/lastblockid
>>> response['lastblockid']
'38658e80x1fb1d'
```

Bridge log:

```bash
INFO:jsonrpcserver.dispatcher.request:{"id": 28, "method": "lastblockid", "jsonrpc": "2.0"}
INFO:jsonrpcserver.dispatcher.response:{"jsonrpc": "2.0", "result": "38658e80x1fb1d", "id": 28}
```
