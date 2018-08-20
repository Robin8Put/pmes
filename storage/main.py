import os
import sys
import logging

# Third-party
import tornado.ioloop

# Locals



logging.basicConfig(filename='storage.log',level=logging.WARNING,
					format='%(asctime)s %(message)s')



if __name__ == '__main__':

	import settings
	print(f"\n\n[+] -- Storage Server started on {settings.storageport} port.")

	from urls import storage_router
	# Define port
	storage_router.listen(settings.storageport)
	# Start server
	tornado.ioloop.IOLoop.current().start()