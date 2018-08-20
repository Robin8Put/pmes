from utils.tornado_components.web import RobustTornadoClient, SignedTornadoClient
import settings


class Permissions:
    """Interact with storage about permissions
    """
    client_storage = SignedTornadoClient(settings.storageurl)

    async def getpermissions(self, **kwargs):
        result = await self.client_storage.request(method_name="getpermissions", **kwargs)
        return result

    async def _changepermissions(self, **kwargs):
        result = await self.client_storage.request(method_name="changepermissions", **kwargs)
        return result