import os
import sys
import logging




host = "http://127.0.0.1"

amsport = 8000
storageport = 8001
pdmsport = 8003
bridgeport = 8004
balanceport = 8005
historyport = 8006

ENDPOINTS = {
	#Public API(get data for new account)
	"ams": r"/api/accounts",       
	#Get accounts data
	"account": r"/api/accounts/([a-zA-Z0-9]+?)",
	#Get/Post balance
	"balance": r"/api/accounts/([a-zA-Z0-9]+?)/balance",
	# GET/POST news for account
	"news": r"/api/accounts/([a-zA-Z0-9]+?)/news",  
	#GRUD data with blockchain
	"blockchain_data": r"/api/blockchain/data", 
	# GET/POST/PUT content price
	"price":r"/api/blockchain/data/price", 
	#Get last block id 
	"lastblockid": r"/api/blockchain/lastblockid",
	#GRUD owner by cid
	"owner": r"/api/blockchain/owner",
	#Get/POST content description
	"description": r"/api/blockchain/description",
	#GRUD content description
	"access_string": r"/api/blockchain/access_string",
	#Sale with blockchain
	"sale": r"/api/blockchain/sale",
	#Make offer
	"make_offer": r"/api/blockchain/make_offer",
	#Accept offer
	"accept_offer": r"/api/blockchain/accept",
	#Reject offer
	"reject_offer": r"/api/blockchain/reject",
	#History server
	"history_server": r"/api/history",
	#Balance server
	"balance_server": r"/api/balance",
	#Dridge server
	"bridge_server": r"/api/bridge",
	#Storage server
	"storage_server": r"/api/storage"
}

storage_url = "%s:%s%s" % (host, storageport, ENDPOINTS["storage_server"])

balance_url = "%s:%s%s" % (host, balanceport, ENDPOINTS["balance_server"])

bridge_url = "%s:%s%s" % (host, bridgeport, ENDPOINTS["bridge_server"]) 

DBNAME = "pmes"
COLLECTION = "accounts"
NEWS = "news"
CID = "cid"
