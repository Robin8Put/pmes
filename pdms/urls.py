from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import RobustTornadoClient, SignedTornadoClient
import tornado.web
import settings
from pdms import views


context = dict(client_storage=SignedTornadoClient(settings.storageurl), 
               client_balance=SignedTornadoClient(settings.balanceurl),
               client_email=RobustTornadoClient(settings.emailurl),
               client_bridge=SignedTornadoClient(settings.bridgeurl))
              

endpoints = [
          (settings.ENDPOINTS["allcontent"],  views.AllContentHandler,  context),
          (settings.ENDPOINTS["content"],     views.ContentHandler,     context),
          (settings.ENDPOINTS["description"], views.DescriptionHandler, context),
          (settings.ENDPOINTS["price"],       views.PriceHandler,       context),
          (settings.ENDPOINTS["deal"],        views.DealHandler,        context),
          (settings.ENDPOINTS["write-access-offer"],views.WriteAccessOfferHandler,context),
          (settings.ENDPOINTS["read-access-offer"],views.ReadAccessOfferHandler,context),
          (settings.ENDPOINTS["reviews"],views.ReviewsHandler,context),
          (settings.ENDPOINTS["review"],views.ReviewHandler,context),
          (settings.ENDPOINTS["deals"],views.DealsHandler,context)

          ]

pdms_router = tornado.web.Application(endpoints, debug=settings.DEBUG)