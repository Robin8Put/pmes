import os
import sys
import logging

# Third-party
import tornado.ioloop
import tornado.wsgi
import wsgiref.simple_server




import settings

logging.basicConfig(filename='balance.log',level=logging.DEBUG,
								format='%(asctime)s %(message)s')


if __name__ == '__main__':

	from urls import balance_router

	# Define port
	balance_router.listen(settings.balanceport)
	print(f"\n[+] -- Balance server started on {settings.balanceport}.")

	# Start server
	tornado.ioloop.IOLoop.current().start()
