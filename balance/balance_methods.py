from pymongo import MongoClient
from jsonrpcserver.aio import methods
from qtum import Qtum

client = MongoClient('localhost', 27017)
db = client.address_balance
accounts = db.accounts
availablecoinid = ["BTC", "QTUM", "LTC", "ETH"]

@methods.add
async def test():
    return 'It works'


@methods.add
async def post_test(car):
    return 'Your car is %s' % car


@methods.add
async def addaddr(address, coinid, uid):
    if Qtum.is_valid_address(address):
        if coinid.upper() in availablecoinid:
            try:
                uid = int(uid)
                account = accounts.find_one({"address": address})
                if account:
                    return "address is in database already"
                else:
                    account = {
                        "address": address,
                        "coinid": coinid,
                        "amount": 0,
                        "uid": uid,
                    }
                    accounts.insert_one(account)
                    client.close()

                    return "address added to database"
            except ValueError:
                return "uid is not integer"
        else:
            return "coinid is not available now"
    else:
        return "address is not valid"


@methods.add
async def incbalance(address, amount):
    amount = float(amount)
    account = accounts.find_one({"address": address})

    if account:
        prev_amount = float(account['amount'])
        new_amount = prev_amount + amount

        accounts.find_one_and_update(
            {"address": address}, {"$set": {"amount": new_amount}})

    else:
        return "Address is not available"

    return {address: new_amount}


@methods.add
async def decbalance(address, amount):
    amount = float(amount)
    account = accounts.find_one({"address": address})

    if account:
        prev_amount = float(account['amount'])
        new_amount = prev_amount - amount

        accounts.update_one_and_update(
            {"address": address}, {"$set": {"amount": new_amount}})

    else:
        return "Address in not available"

    return {address: new_amount}



@methods.add
async def getbalance(uid):
    balance = {}
    bios_collection = accounts.find(
        {"uid": uid}, {"address": 1, "amount": 1})
    for doc in bios_collection:
        address = doc['address']
        amount = doc['amount']
        balance[address] = amount

    return balance

