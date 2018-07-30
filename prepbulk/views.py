# Builtins
import re
import json
import time
import logging
import datetime
import string
from random import choice
from hashlib import sha256

#Third-party
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient


# Locals
import settings
from utils.tornado_components import web 
from utils.tornado_components.timestamp import get_time_stamp 
from utils.tornado_components.web import RobustTornadoClient
from utils.models.account import Account
from utils.pagination import Paginator



methods = {
	"get_all_content": "%s:8000%s" % (settings.host, settings.ENDPOINTS["allcontent"])
}
class BulkHandler(tornado.web.RequestHandler):

	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "Content-Type")
		self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')


	async def post(self):
		http_client = AsyncHTTPClient()
		try:
		    response = await http_client.fetch(methods["get_all_content"])
		except Exception as e:
		    self.write("Error: %s" % e)
		else:
		    self.write(response.body)


	def options(self, uid):
		self.write(json.dumps(["POST"]))


