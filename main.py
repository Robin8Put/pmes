import sys
import os
import logging
import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.routing import RuleRouter, Rule, PathMatches

from ams.urls import ams_router
from pdms.urls import pdms_router


router = RuleRouter([
	Rule(PathMatches("/api/accounts.*"), ams_router),
	Rule(PathMatches("/api/blockchain.*"), pdms_router)
])

if __name__ == '__main__':
	logging.basicConfig(filename='pmes.log',level=logging.DEBUG,
					format='%(asctime)s %(message)s')


	server = HTTPServer(router)
	server.listen(8000)
	tornado.ioloop.IOLoop.current().start()