import tornado.ioloop
import tornado.web
import json, time
from jsonrpcserver import dispatch
from models import Table


def sendmail(text):
    # check optional params on type
    if type(text["optional"]) != list or not text:
        return "Error optional"
    # write data and time for identification to db and give result
    try:
        # add time in text
        text["time"] = time.time()

        # connect to db
        db = Table("email", "email")

        # insert data + time
        data = db.insert(**text)
        return "Success"
    except:
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
            self.write(response)
        else:
            self.write("Invalid method")


def make_app():
    return tornado.web.Application([
        (r"/", HistoryHandler),
    ])


if __name__ == "__main__":
    # run tornado server
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
