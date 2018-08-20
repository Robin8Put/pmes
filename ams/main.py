import os
import sys
import logging

# Third-party
import tornado.ioloop



logging.basicConfig(filename='ams.log',level=logging.DEBUG,
					format='%(asctime)s %(message)s')


if __name__ == '__main__':
	import settings
	print(f"\n\n[+] -- AMS Server started on {settings.pmesport} port.")
	from urls import ams_router
	# Define port
	ams_router.listen(settings.pmesport)
	# Start server
	tornado.ioloop.IOLoop.current().start()
	