from pymongo import MongoClient


pmes = MongoClient()["pmes"]
qtum = MongoClient()["QTUM"]
eth = MongoClient()["ETH"]
put = MongoClient()["PUT"]


pmes["accounts"].remove()
pmes["news"].remove()
pmes["autoincrement"].remove()

qtum["wallet"].remove()
qtum["balance"].remove()
qtum["offer"].remove()
qtum["content"].remove()
qtum["review"].remove()
qtum["deal"].remove()

eth["wallet"].remove()
eth["balance"].remove()
eth["offer"].remove()
eth["content"].remove()
eth["review"].remove()
eth["deal"].remove()


put["wallet"].remove()
put["balance"].remove()
put["offer"].remove()
put["content"].remove()
put["review"].remove()
put["deal"].remove()


