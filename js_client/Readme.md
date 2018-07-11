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
