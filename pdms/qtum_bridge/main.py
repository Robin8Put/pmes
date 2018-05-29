import os
import sys
import logging

# Third-party
import tornado.ioloop

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if PROJ_DIR not in sys.path:
	sys.path.append(PROJ_DIR)

logging.basicConfig(filename='bridge.log',level=logging.DEBUG,
					format='%(asctime)s %(message)s')


if __name__ == '__main__':
	import settings
	from urls import bridge_router
	# Define port
	bridge_router.listen(settings.bridgeport)
	# Start server
	tornado.ioloop.IOLoop.current().start()