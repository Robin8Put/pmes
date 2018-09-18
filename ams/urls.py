import tornado.web
import settings
import views



endpoints = [
		  (settings.ENDPOINTS["withdraw"],      views.WithdrawHandler),
          (settings.ENDPOINTS["ams"],           views.AMSHandler),
          (settings.ENDPOINTS["account"],       views.AccountHandler),
          (settings.ENDPOINTS["news"],          views.NewsHandler),
          (settings.ENDPOINTS["output_offers"], views.OutputOffersHandler),
          (settings.ENDPOINTS["input_offers"],  views.InputOffersHandler),
          (settings.ENDPOINTS["contents"],      views.ContentsHandler),
          ]

if settings.DEBUG:
  endpoints.append((r"/api/accounts/(\d+)/balance", views.BalanceHandler))




ams_router = tornado.web.Application(endpoints, debug=settings.DEBUG)



