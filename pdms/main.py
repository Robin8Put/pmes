import os
import sys
import logging

# Third-party
import tornado.ioloop




logging.basicConfig(filename='pdms.log',level=logging.WARNING,
					format='%(asctime)s %(message)s')


if __name__ == '__main__':
	import settings
	print(f"\n\n[+] -- PDMS Server started on {settings.pdmsport} port.")
	from urls import pdms_router
	# Define port
	pdms_router.listen(settings.pdmsport)
	# Start server
	tornado.ioloop.IOLoop.current().start()
	