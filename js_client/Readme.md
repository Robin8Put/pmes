# JS client

These utilities used for generating public / private keys / blockchain address and sign / verify messages.

There are the following modules in the src folder:

- `bip32keys` --- library for generate public / private keys and sign / verify messages
    - `doGenerate` --- generate public (compressed and uncompresed), wif, private keys and QTUM address. flag show does mainnet or testnet used.
    - `privateKeyToWif` - convert private key to wif format
    - `deriveQtumAddress` - get Qtum address from public key
- `bip39keys` --- library for generate public / private keys and sign / verify messages
    - `generateMnemonic` --- return mnemonic
    - `generateKeysFromMnemonic` --- return public and private keys, QTUM address, wif
- `pmesUtils` --- library for generate public / private keys and sign / verify messages
    - `fromMnemonic` --- return public and private keys from mnemonic
    - `doSign` --- sign message with private_key
    - `doVerify` --- verify message with signature and public_key
    - `encryptProfile` --- encrypt profile with private key using sha256
    - `decryptProfile` --- decrypt profile with private key using sha256
    - `encryptPassword` --- encrypt password with private key using sha256
    - `decryptPassword` --- decrypt password with private key using sha256
    - `decryptProfileByHash` --- decrypt profile with password hash using sha256
- `walletInfo` --- library for generate public / private keys and sign / verify messages
    - `getTxHistory` --- return transaction history by address
    - `getBalance` --- return QTUM balance by address
    - `getQrcBalance` --- return QRC tokens balance by address
- `walletTransactions` --- library for generate public / private keys and sign / verify messages
    - `generateTx` --- generate transaction to send QTUM coins from one address to another
    - `sendRawTx` --- send transaction to the QTUM testnet
    - `generateSendToContractTx` --- generate transaction to send QRC tokens from one address to another
    - `generateCreateContractTx` --- generate transactions for creating contracts

`index.html` import all these modules.

## Encryption details

`encryptProfile` and `decryptProfile` functions was used for few cases:

1. encrypt public and private keys before storing them to the keystore file.

    Keystore file should contains encrypted public and private keys.

    In this case:

    `private_key` - is password for encrypt data to the keystore file

    `content` - is the following JSON string:

```bash
    {
        "pub_key": "qdjdfbfjbfh",
        "priv_key": "sssfsffef"
    }
```

2. encrypt profile before writing it to the blockchain:

    `private_key` - is user's private key

    `content` - is profile

## Installation

Open terminal and run the following commands in the js_client project folder:

```bash
    sudo apt install npm
    npm install
    sudo npm install -g webpack webpack-cli
    webpack --config webpack.config.js
```

## Running

For running JS client make the following actions:

- open `index.html` in the browser
- click on the right button
- choose "Inspect element" item
- open "Console" tab
- expand "Object" item

Then you will see the all available commands:

```bash
    decryptPassword
    decryptProfile
    decryptProfileByHash
    deriveQtumAddress
    doGenerate
    doSign
    doVerify
    encryptPassword
    encryptProfile
    fromMnemonic
    ...
```
