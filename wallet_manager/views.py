# Built-ins
import os
import sys
import json
import logging

# Third-party 
import tornado.ioloop
import tornado.web
from jsonrpcserver.aio import methods

# Locals
import handler



class MainRequestHandler(tornado.web.RequestHandler):   # inherited from local abstract class

    async def get(self):
        method = self.get_query_argument('method')
        params = {k: self.get_argument(k) for k in self.request.arguments if k != 'method'}

        response = await methods.dispatch({"jsonrpc": "2.0", "method": method, 
        									'params': params, "id": "null"})
        self.write(response)

    async def post(self):
        body = self.request.body.decode()
        response = await methods.dispatch(body)
        self.write(response)

