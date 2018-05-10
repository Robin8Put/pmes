"""
Main module
Starts server
"""
import sys
import os
import logging
import tornado.ioloop
# Module with entire endpoints
from endpoints import router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not BASE_DIR in sys.path:
	sys.path.append(BASE_DIR)
else:
	pass


logging.basicConfig(filename='history_storage.log',level=logging.DEBUG,
					format='%(asctime)s %(message)s')

if __name__ == '__main__':
	# Define port
	router.listen(8002)
	# Start server
	tornado.ioloop.IOLoop.current().start()