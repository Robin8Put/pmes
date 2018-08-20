import tornado.web
import settings
import views

              

endpoints = [
          (settings.ENDPOINTS["allcontent"],  views.AllContentHandler),
          (settings.ENDPOINTS["content"],     views.ContentHandler),
          (settings.ENDPOINTS["description"], views.DescriptionHandler),
          (settings.ENDPOINTS["price"],       views.PriceHandler),
          (settings.ENDPOINTS["deal"],        views.DealHandler),
          (settings.ENDPOINTS["write-access-offer"],views.WriteAccessOfferHandler),
          (settings.ENDPOINTS["read-access-offer"],views.ReadAccessOfferHandler),
          (settings.ENDPOINTS["reviews"],views.ReviewsHandler),
          (settings.ENDPOINTS["review"],views.ReviewHandler),
          (settings.ENDPOINTS["deals"],views.DealsHandler)

          ]

pdms_router = tornado.web.Application(endpoints, debug=settings.DEBUG)