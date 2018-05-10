import tornado.web
import settings
from ams.storage import views

router = tornado.web.Application([
        	(r"/*", views.StorageHandler)
        ])