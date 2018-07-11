import modulebip32 from './bip32keys'
import modulebip39 from './bip39keys'
import modulepmesUtils from './pmesUtils.js'
import modulewalletInfo from './walletInfo'
import modulewalletTransactions from './walletTransactions'

export default {
  ...modulebip32,
  ...modulebip39,
  ...modulepmesUtils,
  ...modulewalletInfo,
  ...modulewalletTransactions
}
