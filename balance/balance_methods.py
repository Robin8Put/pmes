import logging
import json
import os
from tornado.ioloop import IOLoop
from motor.motor_tornado import MotorClient
from jsonrpcserver.aio import methods
from qtum_utils.qtum import Qtum
from jsonrpcclient.tornado_client import TornadoClient
import settings


def verify(func):
    async def wrapper(*args, **kwargs):
        with open(os.path.join(settings.BASE_DIR, "keys.json")) as f:
            keys = json.load(f)

        pubkey = keys["pubkey"]

        message = kwargs.get("message")
        signature = kwargs.get("signature")
        try:
            flag = Qtum.verify_message(message, signature, pubkey)
        except:
            flag = None
        if not flag:
            result =  {"error":403, "reason":"Invalid signature"}
        else:
            result = await func(*args, **kwargs)
        return result
    return wrapper


class Balance(object):

    @verify
    async def addaddr(self, *args, **kwargs):
        """ Adding wallet address to database """

        message = json.loads(kwargs.get("message"))

        address = message.get("address")
        coinid = message.get("coinid")
        uid = message.get("uid")

        client = MotorClient()
        db = client[settings.DBNAME]
        balances = db[settings.BALANCE]

        # check if required parameters exist
        if not all([address, coinid, uid]):
            return {"error":400,
                    "reason": "Missed required fields"}
        # Validate coin and address
        if coinid.upper() not in settings.AVAILABLE_COIN_ID:
            return {"error":400,
                    "reason":"Address or coin is not valid"}
        # Check if current address does exist    
        balance = await balances.find_one({"address": address})
        if balance:
            return {"error":400,
                    "reason": "Current address does exist."}
        # Create new wallet
        new_balance = {
            "address": address,
            "coinid": coinid,
            "amount": 0,
            "uid": uid,
        }
        res = await balances.insert_one(new_balance)
        return {"created":"ok"}
        

    @verify
    async def incbalance(self, *args, **kwargs):
        """ Increments users balance """

        message = json.loads(kwargs.get("message", "{}"))

        address = message.get("address")
        amount = int(message.get("amount", 0))
        uid = message.get("uid")

        client = MotorClient()
        db = client[settings.DBNAME]
        balances = db[settings.BALANCE]
        # Check if required fields 

        if not uid and not address:
            return {"error":400,
                    "reason":"Mised required fields or amount is not digit"}
        # Check if avount

        if not amount:
            return {"error":400, "reason":"Funds is zero"}
        
        # Get account by uid or address
        if uid:
            balance = await balances.find_one({"uid": int(uid)})
            logging.debug(balance)
        elif address:
            balance = await balances.find_one({"address": address})
        # Increment balance if accoutn exists
        if not balance:
            return {"error":404, "reason":"Not found"}

        await balances.find_one_and_update(
            {"address": balance["address"]}, {"$inc": {"amount": amount}})
        result = await balances.find_one({"address":balance["address"]})
        # Update users level
        client_storage = TornadoClient(settings.storageurl)
        account = await client_storage.request(method_name="getaccountdata",
                                                **{"id":balance["uid"]})
        if "error" in account.keys():
            return {"error":500,
                    "reason":"While incrementing balance current user was not found"}
        if int(account["level"]) == 2: 
            await client_storage.request(method_name="updatelevel",
                                    **{"id":account["id"], "level":3})
        # Send mail to user
        if account.get("email"):
            client_email = TornadoClient(settings.emailurl)
            email_data = {
                    "to": account["email"],
                    "subject": "Robin8 Support",
                    "optional": "You`ve got %s tokens. Now your balance is %s" %(
                                amount/pow(10,8), int(result["amount"]) / pow(10,8)) 
                }
            await client_email.request(method_name="sendmail", **email_data)

        # Return result
        result = {i:result[i] for i in result if i != "_id"}
        result["amount"] = int(result["amount"]) 
        return result


    @verify
    async def decbalance(self, *args, **kwargs):
        """ Decrements users balance """

        message = json.loads(kwargs.get("message", "{}"))

        uid = message.get("uid")
        address = message.get("address")
        amount = int(message.get("amount", 0))

        client = MotorClient()
        db = client[settings.DBNAME]
        balances = db[settings.BALANCE]
        # Check if required fields exist
        if not uid and not address:
            return {"error":400,
                    "reason":"Missed required fields or amount is not digit"}
        # check if amount is not 0
     
        if not amount:
            return {"error":400, 
                    "reason":"Funds is zero"}
        # Get account
        if uid:
            balance = await balances.find_one({"uid": int(uid)})
        elif address:
            balance = await balances.find_one({"address": address})
        # Check if balance is enough
        if balance and (int(balance["amount"]) - amount) < 0:
            return {"error":400, 
                    "reason":"Address does not exist or amount is not enough"}
        # Update account
        await balances.find_one_and_update(
            {"address": balance["address"]}, {"$inc": {"amount": -amount}})
        result = await balances.find_one({"address":balance["address"]})
        # Return balance
        balance = {i:result[i] for i in result if i != "_id"}
        balance["amount"] = int(balance["amount"]) 
        return balance


    @verify
    async def getbalance(self, *args, **kwargs):
        """ Returns users balance """


        message = json.loads(kwargs.get("message", "{}"))

        address = message.get("address")
        uid = message.get("uid")

        client = MotorClient()
        db = client[settings.DBNAME]
        balances = db[settings.BALANCE]
        # Check if required parameters exist
        if not address and not uid:
            return {"error":400,
                    "reason":"Missed required fields"}

        if address:
            balance = await balances.find_one({"address": address})
        elif uid:
            balance = await balances.find_one({"uid": uid})
        if not balance:
            return {"error":404,
                    "reason":"Current address does not exist"}

        digit = int(balance["amount"]) 
        return {balance["address"]:digit}


balance = Balance()

@methods.add 
async def addaddr(**params):
    result = await balance.addaddr(**params)
    return result

@methods.add 
async def incbalance(**params):
    result = await balance.incbalance(**params)
    return result 

@methods.add 
async def decbalance(**params):
    result = await balance.decbalance(**params)
    return result 

@methods.add 
async def getbalance(**params):
    result = await balance.getbalance(**params)
    return result
   

