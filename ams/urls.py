from jsonrpcclient.tornado_client import TornadoClient
import tornado.web
import settings
import ams.views


context = dict(client_storage=TornadoClient(settings.storageurl), 
               client_balance=TornadoClient(settings.balanceurl),
               client_email=TornadoClient(settings.emailurl))


ams_router = tornado.web.Application([
        	(settings.ENDPOINTS["ams"], ams.views.AMSHandler, context),
        	(settings.ENDPOINTS["account"], ams.views.AccountHandler, context),
        	(settings.ENDPOINTS["news"], ams.views.NewsHandler, context),
        	(r"/api/accounts/(\d+)/balance", ams.views.BalanceHandler, context)], 
                debug=True)