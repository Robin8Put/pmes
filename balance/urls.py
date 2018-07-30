import tornado.web
from views import MainRequestHandler
import settings



balance_router = tornado.web.Application([
        	(r"/api/balance/*", MainRequestHandler),
        ], debug=settings.DEBUG)
