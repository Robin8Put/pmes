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
import handlers.handler


class MainRequestHandler(tornado.web.RequestHandler):  # inherited from local abstract class

    async def post(self):
        body = self.request.body.decode()

        response = await methods.dispatch(body)
        self.write(response)
