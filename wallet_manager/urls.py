import tornado.web
from views import MainRequestHandler

withdraw_router = tornado.web.Application([
    (r"/api/*", MainRequestHandler),
], debug=True)
