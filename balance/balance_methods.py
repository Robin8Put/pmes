from pymongo import MongoClient
from jsonrpcserver.aio import methods
from qtum import Qtum
from web3.auto import w3
from jsonrpcclient.http_client import HTTPClient

client = MongoClient('localhost', 27017)
db = client.address_balance
accounts = db.accounts
availablecoinid = ["BTC", "QTUM", "LTC", "ETH"]
history_host = "http://192.168.1.184:8002/api/history"
historyhost = HTTPClient(history_host)


@methods.add
async def addaddr(address, coinid, uid, amount=0):

    if w3.isAddress(address) or Qtum.is_valid_address(address):
        if coinid.upper() in availablecoinid:
            try:
                amount = float(amount)
                try:
                    uid = int(uid)
                    account = accounts.find_one({"address": address})
                    if account:
                        return "address is in database already"
                    else:
                        account = {
                            "address": address,
                            "coinid": coinid.upper(),
                            "amount": amount,
                            "uid": uid,
                        }
                        accounts.insert_one(account)
                        client.close()

                        try:
                            historyhost.request(
                                method_name="log",
                                module='123',
                                event="addingaddress",
                                table="AddedAdresses",
                                args=[str(address), str(coinid), str(amount), str(uid)]
                                )
                        except Exception:
                            return "History server is not available"

                        return "address added to database"
                except ValueError:
                    return "uid is not integer"
            except ValueError:
                return "amount is not a float"
        else:
            return "coinid is not available now"
    else:
        return "address is not valid"


@methods.add
async def incbalance(address, amount):
    amount = float(amount)
    account = accounts.find_one({"address": address})

    if amount > 0:
        if account:
            prev_amount = float(account['amount'])
            new_amount = prev_amount + amount

            accounts.find_one_and_update(
                {"address": address}, {"$set": {"amount": new_amount}})

            try:
                historyhost.request(
                    method_name="log",
                    module='123',
                    event="incrementatingbalance",
                    table="incrementatedaddresses",
                    args=[str(address), str(amount)]
                )
            except Exception:
                return "History server is not available"
        else:
            return "Address is not available"

        return {str(address): str(new_amount)}
    else:
        return "Amount is invalid"


@methods.add
async def decbalance(address, amount):
    amount = float(amount)
    account = accounts.find_one({"address": address})

    if amount > 0:
        if account:
            prev_amount = float(account['amount'])
            new_amount = prev_amount - amount
            if new_amount < 0:
                new_amount = 0

            accounts.find_one_and_update(
                {"address": address}, {"$set": {"amount": new_amount}})

            try:
                historyhost.request(
                    method_name="log",
                    module='123',
                    event="decrementatingbalance",
                    table="decrementatedaddresses",
                    args=[str(address), str(amount)]
                )
            except Exception:
                return "History server is not available"

        else:
            return "Address is not available"

        return {address: new_amount}
    else:
        return "amount is invalid"


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


@methods.add
async def removeaddress(address):
    try:
        accounts.remove({"address": address})
        try:
            historyhost.request(
                method_name="log",
                module='123',
                event="removingaddress",
                table="RemovedAdresses",
                args=[str(address)]
            )
        except Exception:
            return "History server is not available"
        return "address was removed "
    except Exception:
        return "address is not in database"


@methods.add
async def settozerobycoinid(coinid):
    if coinid.upper() in availablecoinid:
        accounts.update_many(
            {"coinid": coinid.upper()}, {"$set": {"amount": 0}}
        )
    else:
        return "coinid is not available"
