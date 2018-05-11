from jsonrpcserver.aio import methods
import tornado_components.mongo
import settings
import logging


@methods.add
async def createaccount(params):
	table = tornado_components.mongo.Table(dbname=settings.DBNAME,
										collection=settings.COLLECTION)



	document = table.insert(params)
	
	return params