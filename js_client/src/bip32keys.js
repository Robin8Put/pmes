var curve = "secp256k1"
var sigalg = "SHA256withECDSA"
var qtum_magic_bytes = {
  "mainnet": "3a",
  "testnet": "78"
}
var wif_magic_bytes = {
  "mainnet": "80",
  "testnet": "ef"
}

var base58 = (function(alpha) {
  var alphabet = alpha || '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    base = alphabet.length;
  return {
    encode: function(enc) {
      var encoded = '';
      var enc = bigInt(enc, 16);
      while (!enc.isZero()) {
        var remainder = enc.mod(base);
        enc = enc.divide(base);
        encoded = alphabet[remainder].toString() + encoded;
      }
      return encoded;
    },
    decode: function(dec) { // not tested
      if (typeof dec !== 'string')
        throw '"decode" only accepts strings.';
      var decoded = 0;
      while (dec) {
        var alphabetPosition = alphabet.indexOf(dec[0]);
        if (alphabetPosition < 0)
          throw '"decode" can\'t find "' + dec[0] + '" in the alphabet: "' + alphabet + '"';
        var powerOf = dec.length - 1;
        decoded += alphabetPosition * (Math.pow(base, powerOf));
        dec = dec.substring(1);
      }
      return decoded;
    }
  };
})();

var privateKeyToWif = function(privateKey, isMainnet) {
  var prefix = isMainnet ? wif_magic_bytes["mainnet"] : wif_magic_bytes["testnet"]
  var output = prefix + privateKey + '01'; // \x01 - compressed wif
  var extendedPrivateKey = output;
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(output);
  output = sha256.digest();
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(output);
  output = sha256.digest();
  var checksum = output.substr(0, 8);
  output = extendedPrivateKey + checksum;
  output = base58.encode(output);
  return output;

}
// generate qtum wallet address from public key
var deriveQtumAddress = function(publicKey, isMainnet) {
  var output;
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(publicKey)
  output = sha256.digest()
  var md5 = new KJUR.crypto.MessageDigest({
    alg: "ripemd160",
    prov: "cryptojs"
  });
  md5.updateHex(output)
  output = md5.digest()
  var mb = isMainnet ? qtum_magic_bytes["mainnet"] : qtum_magic_bytes["testnet"]
  output = mb + output
  var extended_ripmd160 = output
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(output)
  output = sha256.digest()
  var sha256 = new KJUR.crypto.MessageDigest({
    alg: "sha256",
    prov: "cryptojs"
  });
  sha256.updateHex(output)
  output = sha256.digest()
  var checksum = output.substr(0, 8);
  output = extended_ripmd160 + checksum;
  output = base58.encode(output);
  return output;

}
// generate keys object
// flag show does mainnet or testnet used
var doGenerate = function(flag) {
  var ec = new KJUR.crypto.ECDSA({
    "curve": curve
  });
  var keypair = ec.generateKeyPairHex();
  var pubkey = keypair.ecpubhex;
  var prefix = parseInt(pubkey[pubkey.length - 1], 16) % 2 ? "03" : "02";
  var compressed_pubkey = prefix + pubkey.substr(2, 64);

  return {
    prvkey1: keypair.ecprvhex,
    uncompressed_pubkey: pubkey,
    compressed_pubkey: compressed_pubkey,
    wif: privateKeyToWif(keypair.ecprvhex, flag),
    qaddr: deriveQtumAddress(compressed_pubkey, flag) // passing compressed form of public key
  }
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
  doGenerate,
  privateKeyToWif,
  deriveQtumAddress
}
