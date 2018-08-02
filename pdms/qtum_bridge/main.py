import os
import sys
import logging
from config import blockchain_type

# Third-party
import tornado.ioloop

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if PROJ_DIR not in sys.path:
	sys.path.append(PROJ_DIR)

logging.basicConfig(filename='bridge.log',level=logging.WARNING,
					format='%(asctime)s %(message)s')


if __name__ == '__main__':

	sys.path.append(os.path.abspath(__file__))
	import settings
	from urls import bridge_router
	# Define port
	if blockchain_type == 'qtum':
		bridge_router.listen(settings.bridgeport)
	elif blockchain_type == 'eth':
		bridge_router.listen(settings.ethport)
	# Start server
	tornado.ioloop.IOLoop.current().start()
