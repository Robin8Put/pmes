import tornado.ioloop
import tornado.web
from jsonrpcserver.aio import methods
import balance_methods
import logging
import os
import sys


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        method = self.get_query_argument('method')
        params = {k: self.get_argument(k) for k in self.request.arguments if k != 'method'}
        print(params)
        response = await methods.dispatch({"jsonrpc": "2.0", "method": method, 'params': params, "id": "null"})
        self.write(response)

    async def post(self):
        data = self.request.body.decode()
        print(data)
        response = await methods.dispatch(data)
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if PROJ_DIR not in sys.path:
        sys.path.append(PROJ_DIR)
        
    logging.basicConfig(filename='balance.log',level=logging.DEBUG,
                    format='%(asctime)s %(message)s')

    import settings
    app = make_app()
    app.listen(settings.balanceport)
    tornado.ioloop.IOLoop.current().start()