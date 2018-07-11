function getTxHistory(address) {
    return new Promise((res, rej) => {
      axios.get(`https://testnet.qtum.org/insight-api/txs/?address=${address}`,
      ).then((response) => {
          res(response.data)
        }).catch(err => {
          rej(err)
      })
    })
}
function getBalance(address) {
    return new Promise((res, rej) => {
      http.get(`https://testnet.qtum.org/insight-api/addr/${address}/balance`).then((response) => {
          res(response)
        }).catch(err => {
          rej(err)
      })
    })
}
function getQrcBalance(address) {
  return new Promise((res, rej) => {
    http.get(`https://testnet.qtum.org/insight-api/erc20/balances?balanceAddress=${address}`).then((response) => {
        res(response)
      }).catch(err => {
        rej(err)
    })
  })
}



export default {
  getTxHistory,
  getBalance,
  getQrcBalance
}
