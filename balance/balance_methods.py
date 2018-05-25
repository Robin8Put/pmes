import logging
import json
from pymongo import MongoClient
from jsonrpcserver.aio import methods
from qtum import Qtum
from jsonrpcclient.http_client import HTTPClient
import settings

client = MongoClient('localhost', 27017)
db = client[settings.DBNAME]
accounts = db[settings.BALANCE]
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
async def incbalance(amount=0, uid=None, address=None):
    amount = int(amount * pow(10,8))
    # Get account by uid or address
    if uid:
        account = accounts.find_one({"uid": uid})
    elif address:
        account = accounts.find_one({"address": address})
    # Increment balance if accoutn exists
    if account:
        accounts.find_one_and_update(
            {"address": account["address"]}, {"$inc": {"amount": amount}})
        result = accounts.find_one({"address":account["address"]})

    else:
        return "Uid is not available"

    # Send mail to user
    accountclient = HTTPClient(settings.storageurl)
    user = accountclient.request(method_name="getaccountdata", 
                    **{"id":account["uid"]})
    # If user not found
    if "error" in user.keys():
        return {"error":404, "reason":"Not found"}

    emailclient = HTTPClient(settings.emailurl)
    result = accounts.find_one({"uid": account["uid"]})
    balance = int(result["amount"]) / pow(10,8)
    array = {"to": user["email"],
             "subject": "Robin8 support",
             "optional": "To your balance was added %s. No you have %s." % (
                                amount / 10**8, balance),
             }
    emailclient.request(method_name="sendmail", **array)

    # Update users level
    if int(user["level"]) == 2: 
        accountclient.request(method_name="updatelevel",
                                **{"id":account["uid"], "level":3})
    return {i:result[i] for i in result if i != "_id"}


@methods.add
async def decbalance(amount=0, uid=None, address=None):
    amount = int(amount) * pow(10,8)
    if uid:
        account = accounts.find_one({"uid": uid})
    elif address:
        account = accounts.find_one({"address": address})

    if account and (float(account["amount"]) - amount) >= 0:
        accounts.find_one_and_update(
            {"address": account["address"]}, {"$inc": {"amount": -amount}})
        result = accounts.find_one({"address":account["address"]})

    else:
        return {"error":400, 
                "reason":"Address does not exist or amount is not enough"}

    return {i:result[i] for i in result if i != "_id"}



@methods.add
async def getbalance(address=None, uid=None):
    if address:
        balance = accounts.find_one({"address": address})
    elif uid:
        balance = accounts.find_one({"uid": uid})
        digit = int(balance["amount"]) 
    if balance:
        return {address or uid:digit}
    else:
        return {"error":404}

