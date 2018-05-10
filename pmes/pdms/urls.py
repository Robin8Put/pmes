import tornado.web
import settings
from pdms import views

router = tornado.web.Application([
        	(settings.ENDPOINTS["blockchain_data"], views.DataHandler),
        	(settings.ENDPOINTS["lastblockid"], views.BlockHandler),
        	(settings.ENDPOINTS["owner"], views.OwnerHandler),
        	(settings.ENDPOINTS["description"], views.DescriptionHandler),
        	(settings.ENDPOINTS["access_string"], views.AccessHandler),
        	(settings.ENDPOINTS["sale"], views.SalesHandler),

        ])