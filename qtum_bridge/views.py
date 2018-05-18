import tornado.ioloop
import tornado.web
from jsonrpcserver.aio import methods
import api_methods
import json
import os
import sys
import logging


def validate_params(params):
    if params is None:
        return
    for k, v in params.items():
        if k == 'cid':
            v = int(v)
            if v < 1:
                raise Exception('Illegal cid parameter')
            params[k] = v
        elif k == 'hash':
            if len(str(v)) < 10 or len(str(v)) > 50:
                raise Exception('Bad hash parameter')
        elif k == 'car':
            if v == 'mazda':
                raise Exception('Test exc')
            params[k] = 'test'


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        print('get')
        method = self.get_query_argument('method')
        params = {k: self.get_argument(k) for k in self.request.arguments if k != 'method'}
        try:
            validate_params(params)

            response = await methods.dispatch({"jsonrpc": "2.0", "method": method, 'params': params, "id": "null"})
            self.write(response)
        except Exception as e:
            data = json.dumps({"jsonrpc": "2.0", "result": {"error": str(e)}, "id": "null"})
            self.set_header('Content-type', 'application/json; charset=UTF-8')
            self.write(data)

    async def post(self):
        data = json.loads(self.request.body.decode())
        params = data.get('params', None)
        try:
            validate_params(params)
            response = await methods.dispatch(data)
            self.write(response)
        except Exception as e:
            data = json.dumps({"jsonrpc": "2.0", "result": {"error": str(e)}, "id": "null"})
            self.set_header('Content-type', 'application/json; charset=UTF-8')
            self.write(data)

