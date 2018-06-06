from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import RobustTornadoClient
import tornado.web
import settings
from pdms import views


context = dict(client_storage=RobustTornadoClient(settings.storageurl), 
               client_balance=RobustTornadoClient(settings.balanceurl),
               client_email=RobustTornadoClient(settings.emailurl),
               client_bridge=RobustTornadoClient(settings.bridgeurl))


pdms_router = tornado.web.Application([
        	(settings.ENDPOINTS["blockchain"],  views.ContentHandler,     context),
          (settings.ENDPOINTS["allcontent"],  views.AllContentHandler,  context),
        	(settings.ENDPOINTS["content"],     views.ContentHandler,     context),
        	(settings.ENDPOINTS["description"], views.DescriptionHandler, context),
          (settings.ENDPOINTS["price"],       views.PriceHandler,       context),
          (settings.ENDPOINTS["deal"],        views.DealHandler,        context),
          (settings.ENDPOINTS["offer"],       views.OfferHandler,       context)], 
                debug=True)