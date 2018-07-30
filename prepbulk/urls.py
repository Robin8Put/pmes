from jsonrpcclient.tornado_client import TornadoClient
import tornado.web
import settings
import prepbulk.views



endpoints = [
          (settings.ENDPOINTS["bulk"], prepbulk.views.BulkHandler),
         ]



router = tornado.web.Application(endpoints, debug=settings.DEBUG)

