from utils.tornado_components.web import RobustTornadoClient, SignedTornadoClient
import settings


class Blockchain:
    """Make request to bridge
    """
    client_bridge = SignedTornadoClient(settings.bridgeurl)

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

    async def make_offer(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="make_offer", *args, **kwargs)
        return result

    async def reject_offer(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="reject_offer", *args, **kwargs)
        return result

    async def add_review(self, *args, **kwargs):
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

    async def get_reviews(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_reviews", *args, **kwargs)
        return result

    async def get_offer(self, *args, **kwargs):
        result = await self.client_bridge.request(method_name="get_offer", *args, **kwargs)
        return result


class Balance:
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

    async def incbalance(self, **params):
        result = await self.client_balance.request(method_name="incbalance",
                                                   **params)
        return result

    async def decbalance(self, **params):
        result = await self.client_balance.request(method_name="decbalance",
                                                   **params)
        return result

    async def getbalance(self, **params):
        result = await self.client_balance.request(method_name="getbalance",
                                                   **params)
        return result

    async def depositbalance(self, **params):
        result = await self.client_balance.request(method_name="depositbalance",
                                              **params)
        return result

    async def undepositbalance(self, **params):
        result = await self.client_balance.request(method_name="undepositbalance",
                                              **params)
        return result

    async def confirmbalance(self, **params):
        result = await self.client_balance.request(method_name="confirmbalance",
                                              **params)
        return result

