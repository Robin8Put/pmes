from utils.tornado_components.web import RobustTornadoClient, SignedTornadoClient
from .account_attributes import Balance, Blockchain, Mail
from .permissions import Permissions
import settings
from qtum_utils.qtum import Qtum 
from bip32keys.r8_ethereum.r8_eth import R8_Ethereum
from bip32keys import bip32addresses
from .genesis import GenesisClass
import logging
from jsonrpcclient.tornado_client import TornadoClient



class Account(GenesisClass):
    balance = Balance()
    blockchain = Blockchain()
    permissions = Permissions()
    mailer = Mail()
    client_storage = SignedTornadoClient(settings.storageurl)
    client_withdraw = TornadoClient(settings.withdrawhost)

    validator = {
            "QTUM": lambda x: Qtum.public_key_to_hex_address(x),
            "ETH": lambda x: R8_Ethereum.public_key_to_checksum_address(x),
            "PUT": lambda x: Qtum.public_key_to_hex_address(x),
        }

    withdraw_address = {
            "PUTTEST": lambda x: bip32addresses.Bip32Addresses.address_to_hex(x),
            "QTUMTEST": lambda x: x
    }

    ident_offer = {0:"read_access", 1:"write_access"}


    async def withdraw_fee(self, coinid):
        if not isinstance(coinid, str):
            return {"error":400, "reason":"Coinid type error. Must be string."}
        fees = {
            "BTCTEST": 0.001*pow(10,8),
            "ETH": 0.01*pow(10,8),
            "QTUMTEST": 0.5*pow(10,8), 
            "PUTTEST": 50*pow(10,8),
            "LTCTEST": 0.05*pow(10,8)
        }
        try:
            fee = fees[coinid]
        except KeyError:
            fee = 0
        return fee



    async def logsource(self, **params):
        try:
            result = await self.client_storage.request(method_name="logsource",
                                                        **params)
        except Exception as e:
            result = {"error":500, "reason": str(e)}
        return result


    async def createaccount(self, **params):
        try:
            result = await self.client_storage.request(method_name="createaccount",
                                                           **params)
        except Exception as e:
            result = {"error":500, "reason": str(e)}
        return result

    async def getaccountdata(self, **params):
        result = await self.client_storage.request(method_name="getaccountdata",
                                                   **params)
        return result

    async def createwallet(self, **params):
        result = await self.client_storage.request(method_name="createwallet",
                                                   **params)
        return result

    async def getnews(self, **params):
        result = await self.client_storage.request(method_name="getnews",
                                                   **params)
        return result

    async def setnews(self, **params):
        result = await self.client_storage.request(method_name="setnews",
                                                   **params)
        return result

    async def getaccountbywallet(self, **params):
        result = await self.client_storage.request(method_name="getaccountbywallet",
                                                   **params)
        return result

    async def updatelevel(self, **params):
        result = await self.client_storage.request(method_name="updatelevel",
                                                   **params)
        return result

    async def insertoffer(self, **params):
        result = await self.client_storage.request(method_name="insertoffer",
                                                   **params)
        return result

    async def getoffer(self, **params):
        result = await self.client_storage.request(method_name="getoffer",
                                                   **params)
        return result

    async def removeoffer(self, **params):
        result = await self.client_storage.request(method_name="removeoffer",
                                                   **params)
        return result

    async def updateoffer(self, **params):
        result = await self.client_storage.request(method_name="updateoffer",
                                                   **params)
        return result

    async def mailedconfirm(self, **params):
        result = await self.client_storage.request(method_name="mailedconfirm",
                                                   **params)
        return result

    async def getoffers(self, **params):
        result = await self.client_storage.request(method_name="getoffers",
                                                   **params)
        return result

    async def getuserscontent(self, **params):
        result = await self.client_storage.request(method_name="getuserscontent",
                                                   **params)
        return result

    async def setuserscontent(self, **params):
        result = await self.client_storage.request(method_name="setuserscontent",
                                                   **params)
        return result

    async def updateuserscontent(self, **params):
        result = await self.client_storage.request(method_name="updateuserscontent",
                                                   **params)
        return result

    async def getallcontent(self):
        result = await self.client_storage.request(method_name="getallcontent")
        return result

    async def getsinglecontent(self, cid):
        result = await self.client_storage.request(method_name="getsinglecontent",
                                                   cid=cid)
        return result

    async def changecontentowner(self, **params):
        result = await self.client_storage.request(method_name="changecontentowner",
                                                   **params)
        return result

    async def setaccessstring(self, **params):
        result = await self.client_storage.request(method_name="setaccessstring",
                                                   **params)
        return result

    
    async def getreviews(self, **params):
        result = await self.client_storage.request(method_name="getreviews",
                                             **params)
        return result

    
    async def setreview(self, **params):
        result = await self.client_storage.request(method_name="setreview",
                                             **params)
        return result

    
    async def updatereview(self, **params):
        result = await self.client_storage.request(method_name="updatereview",
                                             **params)
        return result

    
    async def writedeal(self, **params):
        result = await self.client_storage.request(method_name="writedeal",
                                             **params)
        return result

    
    async def getdeals(self, **params):
        result = await self.client_storage.request(method_name="getdeals",
                                             **params)
        return result

    
    async def updatedescription(self, **params):
        result = await self.client_storage.request(method_name="updatedescription",
                                             **params)
        return result

    
    async def setwriteprice(self, **params):
        result = await self.client_storage.request(method_name="setwriteprice",
                                             **params)
        return result

    
    async def setreadprice(self, **params):
        result = await self.client_storage.request(method_name="setreadprice",
                                             **params)
        return result

    
    async def changeowner(self, **params):
        result = await self.client_storage.request(method_name="changeowner",
                                             **params)
        return result

    
    async def sharecontent(self, **params):
        result = await self.client_storage.request(method_name="sharecontent",
                                             **params)
        return result

    async def get_transactions(self, **params):
        result = await self.client_storage.request(method_name="get_transactions",
                                             **params)
        return result

    async def save_transaction(self, **params):
        result = await self.client_storage.request(method_name="save_transaction",
                                             **params)
        return result

    async def withdraw(self, **params):
        result = await self.client_withdraw.request(method_name="withdraw",
                                             **params)
        return result