import tornado.web
# Request-response handlers module
import views
# Module with database interfaces


router = tornado.web.Application([
    (r"/api/history/*", views.HistoryHandler),
])
