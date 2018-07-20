import os
import sys
import logging



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)



host = "http://127.0.0.1"

pmesport = 8000
storageport = 8001
bridgeport = 8003
balanceport = 8004
historyport = 8005
emailport = 8006

pmeshost = "%s:%s" % (host, pmesport)
storagehost = "%s:%s" % (host, storageport)
bridgehost = "%s:%s" % (host, bridgeport)
balancehost = "%s:%s" % (host, balanceport)
historyhost = "%s:%s" % (host, historyport)
emailhost = "%s:%s" % (host, emailport)



ENDPOINTS = {
	#Public API requests

	# POST new account
	"ams": r"/api/accounts",       
	#GET accounts data
	"account": r"/api/accounts/([a-zA-Z0-9]+?)",
	# GET news
	"news": r"/api/accounts/([a-zA-Z0-9]+?)/news",
	# GET/POST blockchain content
	"content": r"/api/blockchain/([a-zA-Z0-9]+?)/content",
	# GET/POST content description
	"description": r"/api/blockchain/([0-9]+)/description",
	# GET/POST content price
	"price": r"/api/blockchain/([0-9]+)/price",
	# POST/DELETE offer
	"offer": r"/api/blockchain/([a-zA-Z0-9]+?)/offer",
	# POST deal
	"deal": r"/api/blockchain/([a-zA-Z0-9]+?)/deal",

	# json-rpc requests
	"blockchain": r"/api/blockchain",
	"allcontent": r"/api/blockchain/content", 
	"history": r"/api/history",
	"balance": r"/api/balance",
	"bridge": r"/api/bridge",
	"storage": r"/api/storage",
	"email": r"/api/email"
}

storageurl = "%s%s" % (storagehost, ENDPOINTS["storage"])

balanceurl = "%s%s" % (balancehost, ENDPOINTS["balance"])

bridgeurl = "%s%s" % (bridgehost, ENDPOINTS["bridge"])

historyurl = "%s%s" % (historyhost, ENDPOINTS["history"]) 

#emailurl = "%s%s" % (emailhost, ENDPOINTS["email"]) 
emailurl = "%s%s" % (emailhost, ENDPOINTS["email"])


DBNAME = "pmes"
ACCOUNTS = "accounts"
NEWS = "news"
WALLET = "wallet"
BALANCE = "balance"
OFFER = "offer"

AVAILABLE_COIN_ID = ["BTC", "QTUM", "LTC", "ETH"]
