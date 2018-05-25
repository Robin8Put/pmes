import tornado.ioloop
import tornado.web
import json, time
from jsonrpcserver import dispatch
from models import Table
import sys
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not BASE_DIR in sys.path:
    sys.path.append(BASE_DIR)

import settings


def sendmail(text):
    # check optional params on type
    if type(text["optional"]) != str or not text:
        return "Error optional"
    # write data and time for identification to db and give result
    try:
        # add time in text
        text["time"] = time.time()

        # connect to db
        db = Table("email", "email")
        #db.show_db()

        # insert data + time
        data = db.insert(**text)
        #print(data)
        return "Success"
    except:
        pass
        return "Error email"



class HistoryHandler(tornado.web.RequestHandler):
    # handler of RPC requests, accepts jsorpc data
    SUPPORTED_METHODS = ['GET','POST']

    def post(self):
        """Accepts jsorpc post request.
        Retrieves data from request body.
        """
        # type(data) = dict
        data = json.loads(self.request.body.decode())
        # type(method) = str
        method = data["method"]
        # type(params) = dict
        params = data["params"]
        if method == "sendmail":
            response = dispatch([sendmail],{'jsonrpc': '2.0', 'method': 'sendmail', 'params': [params], 'id': 1})
            #self.write(response)
        else:
            pass
            #self.write("Invalid method")


def make_app():
    return tornado.web.Application([
        (settings.ENDPOINTS["email"], HistoryHandler),
    ])


if __name__ == "__main__":
    # run tornado server
    app = make_app()
    app.listen(settings.emailport)
    tornado.ioloop.IOLoop.current().start()
