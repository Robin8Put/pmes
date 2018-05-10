from tornado import ioloop
from jsonrpcclient.tornado_client import TornadoClient


# initialization tornado client
client = TornadoClient('http://localhost:8080/')
# template for parameters
array = {"to": "to@gmail.com",
         "subject": "text",
         "optional": ["New text for you"],
         }
# method api
method = 'sendmail'


# post method and parameters
async def main():
    result = await client.request(method, array)
    return result

# sends JSONRPC
ioloop.IOLoop.current().run_sync(main)
