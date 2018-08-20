import os
import sys
import logging

# Third-party
import tornado.ioloop
import tornado.wsgi
import wsgiref.simple_server




import settings

logging.basicConfig(filename='withdraw.log',level=logging.WARNING,
 								format='%(asctime)s %(message)s')


if __name__ == '__main__':

	from urls import withdraw_router

	# Define port
	withdraw_router.listen(settings.withdrawport)

	# Start server
	tornado.ioloop.IOLoop.current().start()
