from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import RobustTornadoClient, SignedTornadoClient
import tornado.web
import settings
import ams.views


context = dict(client_storage=SignedTornadoClient(settings.storageurl), 
               client_balance=SignedTornadoClient(settings.balanceurl),
               client_bridge=SignedTornadoClient(settings.bridgeurl),
               client_email=RobustTornadoClient(settings.emailurl))

endpoints = [
          (settings.ENDPOINTS["ams"],           ams.views.AMSHandler,          context),
          (settings.ENDPOINTS["account"],       ams.views.AccountHandler,      context),
          (settings.ENDPOINTS["news"],          ams.views.NewsHandler,         context),
          (settings.ENDPOINTS["output_offers"], ams.views.OutputOffersHandler, context),
          (settings.ENDPOINTS["input_offers"],  ams.views.InputOffersHandler,  context),
          (settings.ENDPOINTS["contents"],      ams.views.ContentsHandler,     context),
          ]

if settings.DEBUG:
  endpoints.append((r"/api/accounts/(\d+)/balance", ams.views.BalanceHandler, context))


ams_router = tornado.web.Application(endpoints, debug=settings.DEBUG)



