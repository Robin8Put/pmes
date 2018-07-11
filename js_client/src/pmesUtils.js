import bip39 from 'bip39';
import { deriveQtumAddress, privateKeyToWif } from './bip32keys';
import qtum from 'qtumjs-lib';
import bs58check from 'bs58check';

// generate private and public key from mnemonic
function fromMnemonic(mnemonic) {
  let network = qtum.networks.qtum_testnet
  const seedHex = bip39.mnemonicToSeedHex(mnemonic)

  const hdNode = qtum.HDNode.fromSeedHex(seedHex, network)
  hdNode.keyPair.compressed = false
  const account = hdNode
  const keyPair = account.keyPair


  let publicKey = keyPair.getPublicKeyBuffer().toString('hex')
  let privateKey = keyPair.toWIF()

  return {
    publicKey,
    privateKey
  }
}

// msgl - message
// prvkey - private key
var doSign = function(msgl, prvkey) {
  var prvkey = prvkey;
  var msg1 = msgl;
  var sigValueHex;
  do {
    var sig = new KJUR.crypto.Signature({
      "alg": sigalg
    }); // needs to be initialized again
    sig.init({
      d: prvkey,
      curve: curve
    });
    sig.updateString(msg1);
    sigValueHex = sig.sign();
  } while (sigValueHex[7] != 0 || sigValueHex[75] != 0); // those bytes indicate length of r,s components of signature
  // python ecdsa works only with 64-bit r,s
  // takes 2-3 times to generate needed signature

  return sigValueHex
}

// pubkey - public key
// msg1 - message
// sigval - is a signature
var doVerify = function(pubkey, msg1, sigval) {
  var f1 = document.form1;
  var pubkey = pubkey
  var msg1 = msg1;
  var sigval = sigval
  var sig = new KJUR.crypto.Signature({
    "alg": sigalg,
    "prov": "cryptojs/jsrsa"
  });
  sig.init({
    xy: pubkey,
    curve: curve
  });
  sig.updateString(msg1);
  var result = sig.verify(sigval);
  return result;
}
function encryptProfile(content, private_key) {
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(private_key);
  var password = sha256.digest();
  var encrypted = CryptoJS.AES.encrypt(content, password);
  return encrypted.toString();
}

function decryptProfile(encrypted, private_key) {
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(private_key);
  var password = sha256.digest();
  var decrypted = CryptoJS.AES.decrypt(encrypted, password);
  return hexToAscii(decrypted.toString());
}

function decryptProfileByHash(encrypted, password) {
  var decrypted = CryptoJS.AES.decrypt(encrypted, password);
  return hexToAscii(decrypted.toString());
}


function encryptPassword(private_key, password) {
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(private_key);
  var priv_hash = sha256.digest();
  var encrypted = CryptoJS.AES.encrypt(priv_hash, password);
  return encrypted.toString();
}

function decryptPassword(encrypted, password) {
  var decrypted = CryptoJS.AES.decrypt(encrypted, password);
  return hexToAscii(decrypted.toString());
}

function hexToAscii(str) {
  var hexString = str;
  var strOut = '';
  for (var x = 0; x < hexString.length; x += 2) {
    strOut += String.fromCharCode(parseInt(hexString.substr(x, 2), 16));
  }
  return strOut;
}


export default {
  doSign,
  encryptProfile,
  encryptPassword,
  decryptPassword,
  decryptProfileByHash,
  decryptProfile,
  fromMnemonic,
  doVerify,
  encryptPassword,
  decryptPassword
}
