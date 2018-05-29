import tornado.web
import settings
from qtum_bridge import views 

bridge_router = tornado.web.Application([
        	(settings.ENDPOINTS["bridge"], views.MainHandler),
        ], debug=True)