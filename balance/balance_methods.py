import logging
import json
import os
from tornado.ioloop import IOLoop
from motor.motor_tornado import MotorClient
from jsonrpcserver.aio import methods
from utils.qtum_utils.qtum import Qtum
from jsonrpcclient.tornado_client import TornadoClient
from utils.tornado_components.web import SignedTornadoClient
from utils.bip32keys.r8_ethereum.r8_eth import R8_Ethereum # 
import settings
import string
from random import choice
from utils.models.account import Account 


client = MotorClient()

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

    def __init__(self):
        self.account = Account()

    async def generate_token(self, length=16, chars=string.ascii_letters + string.punctuation + string.digits):
        return "".join(choice(chars) for x in range(0, length))

    coin_ids = settings.AVAILABLE_COIN_ID + ["PUT"]

    create_address = {"QTUM": lambda x: Qtum(x, mainnet=False).get_address(),
                    "ETH": lambda x: R8_Ethereum(x).get_address(),
                    "PUT": lambda x: Qtum(x, mainnet=False).get_address()}


    @verify
    async def addaddr(self, *args, **kwargs):
        """ Adding wallet address to database during account registration 

        Accepts:
            - message (signed dictionary):
                - "uid" - int (id of just created account)

        Returns:
            {"result": "ok"}

        Verified: True
        """
        
        message = json.loads(kwargs.get("message"))

        uid = message.get("uid")

        entropy = await self.generate_token()
        
        for coinid in self.coin_ids:

            client = MotorClient()
            db = client[coinid]
            balances = db[settings.BALANCE]

            # Create wallet
            address = self.create_address[coinid](entropy)
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
                "unconfirmed":0,
                "deposit":0, 
                "txid": None
            }
            await balances.insert_one(new_balance)

        return {"result": "ok"}
        

    #@verify
    async def incbalance(self, *args, **kwargs):
        """ Increments users balance 

        Accepts:
            - message (signed dictionary):
                - "address" - str
                - "amount" - int
                - "uid" - str
                - "coinid" - str

        Returns:
            - dictionary with following fields:
                - "address" - str
                - "coinid" - str
                - "amount" - int
                - "uid" - int
                - "unconfirmed" - int (0 by default)
                - "deposit" - int (0 by default)
                - "txid" - None
                
        """
        # Get data from message
        message = json.loads(kwargs.get("message", "{}"))
        address = message.get("address")
        amount = int(message.get("amount", 0))
        uid = message.get("uid")
        coinid = message.get("coinid")
        txid = message.get("txid")

        # Connect to database
        db = client[coinid]
        balances = db[settings.BALANCE]
        
        # Check if amount
        if not amount:
            return {"error":400, "reason":"Funds is zero"}
        
        # Get account by uid or address
        if uid:
            balance = await balances.find_one({"uid": int(uid)})
        elif address:
            balance = await balances.find_one({"address": address})
        # Increment balance if account exists
        if not balance:
            return {"error":404, "reason":"Increment balance. Balance not found"}

        # Update balance
        if not txid:
            await balances.find_one_and_update(
                {"address": balance["address"]}, {"$inc": {"amount": int(amount)}})
            result = await balances.find_one({"address":balance["address"]})


        else:
            db = client["PUT"]
            balances = db[settings.BALANCE]
            await balances.find_one_and_update(
                {"uid": balance["uid"]}, {"$inc": {"unconfirmed": int(amount)}})
            result = await balances.find_one({"uid":balance["uid"]})
            
            await balances.find_one_and_update(
                {"uid": balance["uid"]}, {"$set": {"txid": txid}})

        account = await self.account.getaccountdata(**{"id":balance["uid"]})

        # Send mail to user
        if account.get("email"):
            email_data = {
                    "to": account["email"],
                    "subject": "Robin8 Support",
                    "optional": "You`ve got %s tokens. Now your balance is %s" %(
                                amount/pow(10,8), int(result["amount"]) / pow(10,8)) 
                }
            await self.account.mailer.sendmail(**email_data)

        # Return result
        result = {i:result[i] for i in result if i != "_id"}
        result["amount"] = int(result["amount"]) 
        return result



    @verify
    async def decbalance(self, *args, **kwargs):
        """ Decrements users balance 
        
        Accepts:
            - message (signed dictionary):
                - "address" - str
                - "amount" - int
                - "uid" - str
                - "coinid" - str

        Returns:
            - dictionary with following fields:
                - "address" - str
                - "coinid" - str
                - "amount" - int
                - "uid" - int
                - "unconfirmed" - int (0 by default)
                - "deposit" - int (0 by default)
                - "txid" - None

        """

        message = json.loads(kwargs.get("message", "{}"))

        uid = message.get("uid")
        address = message.get("address")
        amount = int(message.get("amount", 0))
        coinid = message.get("coinid", "PUT")

        client = MotorClient()
        db = client[coinid]
        balances = db[settings.BALANCE]
        # Check if required fields exist
        if not uid and not address:
            return {"error":400,
                    "reason":"Missed required fields or amount is not digit"}
        # check if amount is not 0
     
        if not amount:
            return {"error":400, 
                    "reason":"Decrement balance. Funds is zero"}
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
            {"uid": balance["uid"]}, {"$inc": {"amount": -amount}})
        result = await balances.find_one({"uid":balance["uid"]})
        # Return balance
        balance = {i:result[i] for i in result if i != "_id"}
        balance["amount"] = int(balance["amount"]) 
        return balance


    @verify
    async def getbalance(self, *args, **kwargs):
        """ Returns users balance 

        Accepts:
            - message (signed dictionary)
                - "address" - str
                - "amount" - int
                - "uid" - str
                - "coinid" - str
        Returns:
            - list of dictionaries with following fields:
                - "address" - str
                - "coinid" - str
                - "amount" - int
                - "uid" - int
                - "unconfirmed" - int (0 by default)
                - "deposit" - int (0 by default)

        Verified: True

        """
        # Get data from messaqe
        message = json.loads(kwargs.get("message", "{}"))

        address = message.get("address")
        uid = message.get("uid")

        # Check if required parameters exist
        if not address and not uid:
            return {"error":400,
                    "reason":"Missed required fields"}

        wallets = []

        # Iter available coin id`s
        for coinid in self.coin_ids:
            logging.debug("\n Coin id")
            logging.debug(coinid)
            # Connect to appropriate database
            db = client[coinid]
            balances = db[settings.BALANCE]
            # Get balance
            if address:
                balance = await balances.find_one({"address": address})
            elif uid:
                balance = await balances.find_one({"uid": uid})
            try:
                wallets.append({"address":balance["address"], "amount":balance["amount"], 
                    "deposit":balance["deposit"], "unconfirmed":balance["unconfirmed"],
                    "coinid":coinid})
            except:
                continue
        if not wallets:
            return {"error":404,
                    "reason":"Current address does not exist"}
        return wallets


    @verify 
    async def depositbalance(self, *args, **kwargs):
        """ Freeze partial balance. 
        Amount equals to offer`s price.

        Accepts:
            - message (sogned dictionary):
                - "address" - str
                - "uid" - str
                - "coinid" - str

        Returns:
                - "address" - str
                - "coinid" - str
                - "amount" - int
                - "uid" - int
                - "unconfirmed" - int (0 by default)
                - "deposit" - int (0 by default)


        Verified: True

        """
        # Get data from request
        message = json.loads(kwargs.get("message", "{}"))

        uid = int(message.get("uid", 0))
        amount = int(message.get("amount", 0))
        coinid = message.get("coinid")

        coinid = "PUT"

        # Connect to database
        db = client[coinid]
        balances = db[settings.BALANCE]

        # Check if current balance exists
        balance = await balances.find_one({"uid":uid})
        if not balance:
            return {"error":404, "reason":"Current user was not found"}     

        # Decrement amount
        updated_amount = await balances.find_one_and_update({"uid":balance["uid"]}, 
                                                            {"$inc":{"amount": -amount}})
        # Increment deposit
        updated_deposit = await balances.find_one_and_update({"uid":balance["uid"]}, 
                                                            {"$inc":{"deposit": amount}})
        updated = await balances.find_one({"uid":balance["uid"]})

        return {i:updated[i] for i in updated if i != "_id" and i != "txid"}


    @verify 
    async def undepositbalance(self, *args, **kwargs):
        """ Returns deposit amount to the base balance
        
        Accepts:
             - message (signed dict):
                - "uid" - str
                - "amount" - int
                - "coinid" - str

        Returns:
                - "address" - str
                - "coinid" - str
                - "amount" - int
                - "uid" - int
                - "unconfirmed" - int (0 by default)
                - "deposit" - int (0 by default)

        Verified: True
        
        """
        # Get data from request
        message = json.loads(kwargs.get("message", "{}"))
        uid = int(message.get("uid", 0))
        amount = int(message.get("amount", 0))
        coinid = message.get("coinid")

        coinid = "PUT"

        # Connect to database
        db = client[coinid]
        balances = db[settings.BALANCE]

        # Try to get current balance
        balance = await balances.find_one({"uid":uid})
        if not balance:
            return {"error":404, "reason":"Current user was not found"}     

        difference = int(balance["deposit"]) - int(amount)
        if difference < 0:
            return {"error":400, 
                    "reason": "Undeposit balance. Can not set value below zero."}
        # Decrement from deposit 
        await balances.find_one_and_update({"uid":balance["uid"]}, 
                                            {"$inc":{"deposit":-amount}})
        # Increment dase balance
        await balances.find_one_and_update({"uid":balance["uid"]}, 
                                            {"$inc":{"amount": amount}})
        # Get just updated balance
        updated = await balances.find_one({"uid":balance["uid"]})

        return {i:updated[i] for i in updated if i != "_id" and i != "txid"}


    #@verify 
    async def confirmbalance(self, *args, **kwargs):
        """ Confirm balance after trading

        Accepts:
            - message (signed dictionary):
                - "txid" - str
                - "coinid" - str
                - "amount" - int

        Returns:
                - "address" - str
                - "coinid" - str
                - "amount" - int
                - "uid" - int
                - "unconfirmed" - int (0 by default)
                - "deposit" - int (0 by default)

        Verified: True

        """
        # Get data from request
        #if message.get()
        message = json.loads(kwargs.get("message", "{}"))

        txid = message.get("txid")
        coinid = message.get("coinid")
        buyer_address = message.get("buyer_address")
        cid = message.get("cid")


        # Check if required fields exists
        if not all([txid, coinid, cid, buyer_address]):
            return {"error":400, "reason": "Confirm balance. Missed required fields"}

        if coinid in settings.AVAILABLE_COIN_ID:
            self.account.blockchain.setendpoint(settings.bridges[coinid])
        offer = await self.account.blockchain.getoffer(cid=cid, buyer_address=buyer_address)

        # Connect to database
        coinid = "PUT"

        database = client[coinid]
        balance_collection = database[settings.BALANCE]

        amount = int(offer["price"])
        # Try to update balance if exists
        updated = await balance_collection.find_one_and_update(
                                {"txid":txid}, {"$inc":{"amount":int(amount)}})
        if not updated:
            return {"error":404, 
                    "reason":"Confirm balance. Not found current transaction id"}

        # Decrement unconfirmed
        await balance_collection.find_one_and_update(
                                {"txid":txid}, {"$inc":{"unconfirmed": -amount}})

        # Update users level if it is equal two
        account = await self.account.getaccountdata(**{"id":updated["uid"]})
        if "error" in account.keys():
            return {"error":500,
                    "reason":"While incrementing balance current user was not found"}

        if int(account["level"]) == 2:
            await self.account.updatelevel(**{"id":account["id"], "level":3})

        return {i:updated[i] for i in updated if i != "_id" and i != "txid"}



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

@methods.add 
async def depositbalance(**params):
    result = await balance.depositbalance(**params)
    return result

@methods.add 
async def undepositbalance(**params):
    result = await balance.undepositbalance(**params)
    return result

@methods.add 
async def confirmbalance(**params):
    result = await balance.confirmbalance(**params)
    return result


   

