from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from models import Table


'''
qtum = AuthServiceProxy("http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018"))

qtgrawt = qtum.getrawtransaction("18bf6d000ce23ac86202ff9293cb8a5ee84d44f447bf982c4c578aad743f9eb9")
qwe = qtum.decoderawtransaction(qtgrawt)
print(qwe)
'''

db_wallet = Table("pars", "wallet6")
print(db_wallet.read("qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis"))
#db_wallet.show_db()
