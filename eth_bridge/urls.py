import tornado.web
import settings
import views 

bridge_router = tornado.web.Application([
        	(settings.ENDPOINTS["bridge"], views.MainHandler),
        ], debug=settings.DEBUG)