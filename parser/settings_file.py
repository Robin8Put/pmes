import os

balance_server = "http://localhost:8004/api/balance"
storghost = "http://localhost:8001/api/storage"
qtum_host_def = "http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018")
address_smart_contract_eth = "0xBc9df82727513A5F14315883A048324A1fAA0788"
address_smart_contract_qtum = ["f984564b93aea2fc9a4bb38a6b0ecf643d3d19aa", "b1b3ea7bb5dd3fdc64b89d9896da63f0e14472c4"]
home = os.path.expanduser("~")
ipc_provider = "{}/.ethereum/rinkeby/geth.ipc".format(home)
