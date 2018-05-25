import tornado.web
import settings
import balance.views



balance_router = tornado.web.Application([
        	(settings.ENDPOINTS["balance"], balance.views.MainHandler),
        ], debug=True)
