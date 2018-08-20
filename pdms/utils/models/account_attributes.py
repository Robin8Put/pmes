from utils.tornado_components.web import RobustTornadoClient, SignedTornadoClient
import settings
from .genesis import GenesisClass
import logging


class Blockchain(GenesisClass):
    """Make request to bridge
    """
    client_bridge = SignedTornadoClient(settings.bridgeurl)

    def setendpoint(self, endpoint):
        self.client_bridge.endpoint = endpoint

    async def lastblockcid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="lastblockid", *args, **kwargs)
        return result

    async def balance(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="balance", *args, **kwargs)
        return result

    async def ipfscat(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="ipfscat", *args, **kwargs)
        return result

    async def getcid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="getcid", *args, **kwargs)
        return result

    async def readbycid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="readbycid", *args, **kwargs)
        return result

    async def ownerbycid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="ownerbycid", *args, **kwargs)
        return result

    async def descrbycid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="descrbycid", *args, **kwargs)
        return result

    async def makecid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="makecid", *args, **kwargs)
        return result

    async def setdescrforcid(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="setdescrforcid", *args, **kwargs)
        return result

    async def last_access_string(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="lastaccessstring", *args, **kwargs)
        return result

    async def changeowner(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="changeowner", *args, **kwargs)
        return result

    async def sellcontent(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="sellcontent", *args, **kwargs)
        return result

    async def setprice(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="setprice", *args, **kwargs)
        return result

    async def getprice(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="getprice", *args, **kwargs)
        return result

    async def makeoffer(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="make_offer", *args, **kwargs)
        return result

    async def rejectoffer(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="reject_offer", *args, **kwargs)
        return result

    async def addreview(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="add_review", *args, **kwargs)
        return result

    async def getallcontent(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="getallcontent", *args, **kwargs)
        return result

    async def getsinglecontent(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="getsinglecontent", *args, **kwargs)
        return result

    async def getuserscontent(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="getuserscontent", *args, **kwargs)
        return result

    async def getreviews(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_reviews", *args, **kwargs)
        return result

    async def getoffer(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_offer", *args, **kwargs)
        return result

    async def getbuyeroffers(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_buyer_offers", *args, **kwargs)
        return result

    async def getcidoffers(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_cid_offers", *args, **kwargs)
        return result

    async def setwriteprice(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="set_write_price", *args, **kwargs)
        return result

    async def setreadprice(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="set_read_price", *args, **kwargs)
        return result

    async def getwriteprice(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_write_price", *args, **kwargs)
        return result

    async def getreadprice(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_read_price", *args, **kwargs)
        return result


class Balance(GenesisClass):
    """Make request to balance
    """
    client_balance = SignedTornadoClient(settings.balanceurl)

    async def addaddr(self, **params):
        result = await self.client_balance.request(method_name="addaddr",
                                                   **params)
        return result

    async def addwallet(self, **params):
        result = await self.client_balance.request(method_name="addwallet",
                                                   **params)
        return result

    async def add_active(self, **params):
        result = await self.client_balance.request(method_name="add_active",
                                                   **params)
        return result

    async def sub_active(self, **params):
        result = await self.client_balance.request(method_name="sub_active",
                                                   **params)
        return result

    async def get_wallets(self, **params):
        result = await self.client_balance.request(method_name="get_wallets",
                                                   **params)
        return result

    async def freeze(self, **params):
        result = await self.client_balance.request(method_name="freeze",
                                              **params)
        return result

    async def unfreeze(self, **params):
        result = await self.client_balance.request(method_name="unfreeze",
                                              **params)
        return result

    async def sub_frozen(self, **params):
        result = await self.client_balance.request(method_name="sub_frozen",
                                              **params)
        return result

    async def add_frozen(self, **params):
        result = await self.client_balance.request(method_name="add_frozen",
                                              **params)
        return result

    async def confirmbalance(self, **params):
        result = await self.client_balance.request(method_name="sub_frozen",
                                              **params)

        result = await self.client_balance.request(method_name="add_active",
                                              **params)
        return result

    async def registerdeal(self, **params):
        result = await self.client_balance.request(method_name="registerdeal",
                                              **params)
        return result


class Mail(GenesisClass):

    client_email = RobustTornadoClient(settings.emailurl)

    async def sendmail(self, **params):
        result = await self.client_email.request(method_name="sendmail", **params)
        return result





