import tornado.web
import settings
import ams.views



ams_router = tornado.web.Application([
        		(settings.ENDPOINTS["ams"], 
        		ams.views.AMSHandler, 
        		dict(storagehost=settings.storageurl, 
        				balancehost=settings.balanceurl)),
        	(settings.ENDPOINTS["account"], 
        		ams.views.AccountHandler,
        		dict(storagehost=settings.storageurl, 
        				balancehost=settings.balanceurl)),
        	(settings.ENDPOINTS["news"], 
        		ams.views.NewsHandler,
        		dict(storagehost=settings.storageurl, 
        				balancehost=settings.balanceurl))
        ], debug=True)