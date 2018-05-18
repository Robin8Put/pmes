import tornado.web
import settings
import balance.views



balance_router = tornado.web.Application([
        	(settings.ENDPOINTS["balance_server"], balance.views.MainHandler),
        ])
