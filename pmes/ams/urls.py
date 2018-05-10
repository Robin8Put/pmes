import tornado.web
import settings
import ams.views

router = tornado.web.Application([
        	(settings.ENDPOINTS["ams"], ams.views.AMSHandler),
        	(settings.ENDPOINTS["account"], ams.views.AccountHandler),
        	(settings.ENDPOINTS["balance"], ams.views.BalanceHandler),
        ])