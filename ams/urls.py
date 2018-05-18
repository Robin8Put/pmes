import tornado.web
import settings
import ams.views



ams_router = tornado.web.Application([
        		(settings.ENDPOINTS["ams"], 
        		ams.views.AMSHandler, 
        		dict(storagehost=settings.storage_url, 
        				balancehost=settings.balance_url)),
        	(settings.ENDPOINTS["account"], 
        		ams.views.AccountHandler,
        		dict(storagehost=settings.storage_url, 
        				balancehost=settings.balance_url)),
        	(settings.ENDPOINTS["balance"], 
        		ams.views.BalanceHandler,
        		dict(storagehost=settings.storage_url, 
        				balancehost=settings.balance_url)),
                (settings.ENDPOINTS["news"],
                        ams.views.NewsHandler,
                        dict(storagehost=settings.storage_url, 
                                        balancehost=settings.balance_url)),
        ])