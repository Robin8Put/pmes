from tornado import ioloop
from jsonrpcclient.tornado_client import TornadoClient


# initialization tornado client
client = TornadoClient('http://localhost:8080/')
# template for parameters
data = 100
list_new = "On your account added {} coin".format(data)
array = {"to": "example_to@gmail.com",
         "subject": "subject",
         "optional": list_new,
         }
# method api
method = 'sendmail'


# post method and parameters
async def main():
    result = await client.request(method, array)
    return result

# sends JSONRPC
ioloop.IOLoop.current().run_sync(main)
