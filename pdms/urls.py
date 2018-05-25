import tornado.web
import settings
from pdms import views



pdms_router = tornado.web.Application([
        	(settings.ENDPOINTS["blockchain"], views.ContentHandler),
                (settings.ENDPOINTS["allcontent"], views.AllContentHandler),
        	(settings.ENDPOINTS["content"], views.ContentHandler),
        	(settings.ENDPOINTS["description"], views.DescriptionHandler),
                (settings.ENDPOINTS["price"], views.PriceHandler),
                (settings.ENDPOINTS["deal"], views.DealHandler),
                (settings.ENDPOINTS["offer"], views.OfferHandler)], 
                debug=True)