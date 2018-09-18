import os
import sys
import logging

# Third-party
import tornado.ioloop
import tornado.wsgi
import wsgiref.simple_server

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

logging.basicConfig(filename='withdraw.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')

if __name__ == '__main__':
    from urls import withdraw_router

    # Define port
    withdraw_router.listen(8011)

    # Start server
    tornado.ioloop.IOLoop.current().start()
