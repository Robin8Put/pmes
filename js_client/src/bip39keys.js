import bip39 from 'bip39';
import { deriveQtumAddress, privateKeyToWif } from './bip32keys';
import qtum from 'qtumjs-lib';
import bs58check from 'bs58check';



function generateMnemonic() {
  return bip39.generateMnemonic()
}


function generateKeysFromMnemonic({mnemonic}) {
  if (bip39.validateMnemonic(mnemonic) == false) throw new Error ("invalid mnemonic")
  let network = qtum.networks.qtum_testnet
  const seedHex = bip39.mnemonicToSeedHex(mnemonic)
  const hdNode = qtum.HDNode.fromSeedHex(seedHex, network)
  const account = hdNode.deriveHardened(88).deriveHardened(0).deriveHardened(0)
  const keyPair = account.keyPair
  keyPair.compressed = false
  let privateKey = bs58check.decode(keyPair.toWIF()).toString('hex')
  privateKey = privateKey.slice(2)
  var curve = "secp256k1"
  var ec = new KJUR.crypto.ECDSA({
    "curve": curve
  });

  var pubkey = ec.ecparams.G.multiply(new BigInteger(privateKey, 16));
  var x = pubkey.getX().toBigInteger().toString(16);
  var y = pubkey.getY().toBigInteger().toString(16);
  var public_key = '04' + x + y
  var prefix = parseInt(public_key[public_key.length - 1], 16) % 2 ? "03" : "02";
  var compressed_pubkey = prefix + x;
  var address = deriveQtumAddress(compressed_pubkey, false)
  let publicKey = public_key
  let wif = privateKeyToWif(privateKey, false)
  return {
    privateKey,
    publicKey,
    address,
    wif
  }
}

export default {
  generateMnemonic,
  generateKeysFromMnemonic
}
