# Builtins
import json
import time
import logging
import datetime
import string
from random import choice
from hashlib import sha256

#Third-party
from jsonrpcserver import dispatch
import tornado.web
import tornado_components.web 
import tornado_components.mongo
from jsonrpcclient.http_client import HTTPClient
from jsonrpcserver.aio import methods
import requests

# Locals
import settings
from tornado_components.rpc_client import RPCClient
from tornado_components.timestamp import get_time_stamp
from qtum_utils.qtum import Qtum


class DataHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles blockchain data manipulations
	"""
	def get(self):
		"""Receives data from blockchain
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make get data response to the bridge
		response = RPCClient.data_from_blockchain(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return result
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish


	def post(self):
		"""Writes data to blockchain
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make write data to blockchain request
		response = RPCClient.postcontent(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return result
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish


class BlockHandler(tornado_components.web.ManagementSystemHandler):
	"""Single blockchain block handler
	"""
	def get(self):
		"""Receives block data
		"""
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Request last block to blockchain
		response = RPCClient.lastblockid(bridgehost)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return block id
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish



class OwnerHandler(tornado_components.web.ManagementSystemHandler):
	"""single address owner handler
	"""
	def get(self):
		"""Receives owners data
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make response to blockchain
		response = RPCClient.getownerbycid(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return owners data
			self.write({"owner":response})
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish

	def put(self):
		"""Change owners data
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make change request to blockchain
		response = RPCClient.changeowner(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return updated owners data
			self.write({"owner":response})
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish


class DescriptionHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles contents descriptions within blockchain
	"""
	def get(self):
		"""Receives content description from blockchain
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make description request to blockchain
		response = RPCClient.getcontentdescr(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return description
			self.write({"description":response})
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish

	def post(self):
		"""Set contents description
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make appropriate request to blockchain
		response = RPCClient.setdescrforcid(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return result
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish


class AccessHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles access marks
	"""
	def get(self):
		"""Get access string
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make access string request to blockchain
		response = RPCClient.last_access_string(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return access string
			self.write({"access_string":response})
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish


class SalesHandler(tornado_components.web.ManagementSystemHandler):
	"""Handles sales events
	"""	
	def post(self):
		"""Sells content
		"""
		# Get parameters from request
		data = { k: self.get_argument(k) for k in self.request.arguments}
		bridgehost = "%s:%s" % (settings.host, settings.bridgeport)
		# Make sell content to blockchain
		response = RPCClient.sellcontent(bridgehost, data)
		try:
			error_code = response["error"]
			error_reason = response["reason"]
		except:
			# Return result
			self.write(response)
		else:
			self.set_status(error_code)
			self.write(error_reason)
			raise tornado.web.Finish

