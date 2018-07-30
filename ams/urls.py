import tornado.web
import settings
import ams.views



endpoints = [
		  (settings.ENDPOINTS["withdraw"],      ams.views.WithdrawHandler),
          (settings.ENDPOINTS["ams"],           ams.views.AMSHandler),
          (settings.ENDPOINTS["account"],       ams.views.AccountHandler),
          (settings.ENDPOINTS["news"],          ams.views.NewsHandler),
          (settings.ENDPOINTS["output_offers"], ams.views.OutputOffersHandler),
          (settings.ENDPOINTS["input_offers"],  ams.views.InputOffersHandler),
          (settings.ENDPOINTS["contents"],      ams.views.ContentsHandler),
          ]

if settings.DEBUG:
  endpoints.append((r"/api/accounts/(\d+)/balance", ams.views.BalanceHandler))




ams_router = tornado.web.Application(endpoints, debug=settings.DEBUG)



