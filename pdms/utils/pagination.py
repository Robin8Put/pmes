from utils.tornado_components.web import SignedHTTPClient
import settings
import logging


class Paginator(object):
	""" Pagination object """

	def __init__(self, coinid, page, limit, cids=None):
		""" Initialize page limit output and last cid
		"""
		self.limit = int(limit)
		self.coinid = coinid
		try:
			self.page = int(page)
		except:
			self.page = None
		self.last_blocks = {}

		if not cids:
			client = SignedHTTPClient(settings.bridges[coinid])
			try:
				cid = client.request(method_name="get_next_cid")["next_cid"]
			except:
				cid = 1
		else:
			cid = len(cids)
		self.last_blocks[coinid] = int(cid) 


	def get_range(self):
		""" Get range """

		if not self.page:
			return (1, self.last_blocks[self.coinid])

		# Get start of the range
		start = self.page * self.limit

		# Get finish of the range
		end = (self.page + 1) * self.limit

		if start > self.last_blocks[self.coinid]:
			return (1,1)
		if end > self.last_blocks[self.coinid]:
			return (start, self.last_blocks[self.coinid])
		return (start, end)

	def get_pages(self):
		if not self.last_blocks[self.coinid] % self.limit:
			return {"pages": self.last_blocks[self.coinid] // self.limit}
		return {"pages": (self.last_blocks[self.coinid] // self.limit) + 1}









