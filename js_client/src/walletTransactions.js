
import qtum from 'qtumjs-lib'

async function generateTx(wallet, to, amount, fee, utxoList) {
  return qtum.utils.buildPubKeyHashTransaction(wallet.keyPair, to, amount, fee, utxoList)
}
function sendRawTx(rawTx) {
  return new Promise((res, rej) => {
    http.get(`https://testnet.qtum.org/tx/send${rawTx}`, { rawtx: rawTx }).then((response) => {
        res(response)
      }).catch(err => {
        rej(err)
    })
  })
}
async function generateSendToContractTx(wallet, contractAddress, encodedData, gasLimit, gasPrice, fee, utxoList) {
  return qtum.utils.buildSendToContractTransaction(wallet.keyPair, contractAddress, encodedData, gasLimit, gasPrice, fee, utxoList)
}
function generateCreateContractTx(wallet, code, gasLimit, gasPrice, fee, utxoList) {
  return qtum.utils.buildCreateContractTransaction(wallet.keyPair, code, gasLimit, gasPrice, fee, utxoList)
}



export default {
  generateTx,
  sendRawTx,
  generateSendToContractTx,
  generateCreateContractTx
}
