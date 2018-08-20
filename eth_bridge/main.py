import os
import sys
import logging
from config import blockchain_type

# Third-party
import tornado.ioloop
import settings


logging.basicConfig(filename='bridge.log',level=logging.DEBUG,
					format='%(asctime)s %(message)s')


if __name__ == '__main__':

	sys.path.append(os.path.abspath(__file__))
	import settings
	print(f"\n\n[+] -- ETH Bridge Server started on {settings.ethport} port.")
	from urls import bridge_router
	# Define port
	if blockchain_type == 'qtum':
		bridge_router.listen(settings.bridgeport)
	elif blockchain_type == 'eth':
		bridge_router.listen(settings.ethport)
	# Start server
	tornado.ioloop.IOLoop.current().start()
