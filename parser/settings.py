import os
import sys
import logging



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

domain = "http://pdms2.robin8.io"

host = "http://127.0.0.1"

pmesport = 8000
storageport = 8001
bridgeport = 8003
ethport = 8007
balanceport = 8004
historyport = 8005
emailport = 8006

pmeshost = "%s:%s" % (host, pmesport)
storagehost = "%s:%s" % (host, storageport)
bridgehost = "%s:%s" % (host, bridgeport)
ethhost = "%s:%s" % (host, ethport)
balancehost = "%s:%s" % (host, balanceport)
historyhost = "%s:%s" % (host, historyport)
emailhost = "%s:%s" % (host, emailport)



ENDPOINTS = {
	#Public API requests

	# POST new account
	"ams": r"/api/accounts",           
	#GET accounts data
	"account": r"/api/accounts/([a-zA-Z0-9]+?)",  
	# GET blockchain content
	"contents": r"/api/accounts/([a-zA-Z0-9]+?)/profiles", 
	# GET all contents reviews
	"reviews": r"/api/blockchain/([a-zA-Z0-9]+?)/([a-zA-Z0-9]+?)/reviews",
	# POST contents review
	"review": r"/api/blockchain/([a-zA-Z0-9]+?)/review",
	# POST, PUT deal
	"deal": r"/api/blockchain/([a-zA-Z0-9]+?)/deal", 
	# GET deals
	"deals": r"/api/blockchain/([a-zA-Z0-9]+?)/deals",
	# GET all users offers
	"output_offers": r"/api/accounts/([a-zA-Z0-9]+?)/output-offers",  
	# GET all users offers
	"input_offers": r"/api/accounts/([a-zA-Z0-9]+?)/input-offers", 
	# POST/PUT right access offer
	"write-access-offer": r"/api/blockchain/([a-zA-Z0-9]+?)/write-access-offer",
	# POST/PUT read access offer
	"read-access-offer": r"/api/blockchain/([a-zA-Z0-9]+?)/read-access-offer",
	# GET news
	"news": r"/api/accounts/([a-zA-Z0-9]+?)/news",   
	# GET all content
	"allcontent": r"/api/blockchain/profile",  
	# GET/POST content description
	"description": r"/api/blockchain/([0-9]+)/description",  
	# GET/POST content price
	"price": r"/api/blockchain/([0-9]+)/price",  
	# GET/POST blockchain content
	"content": r"/api/blockchain/([a-zA-Z0-9]+?)/([a-zA-Z0-9]+?)/profile",    


	"history": r"/api/history",
	"balance": r"/api/balance",
	"bridge": r"/api/bridge",
	"storage": r"/api/storage",
	"email": r"/api/email"
}

storageurl = "%s%s" % (storagehost, ENDPOINTS["storage"])

balanceurl = "%s%s" % (balancehost, ENDPOINTS["balance"])

bridgeurl = "%s%s" % (bridgehost, ENDPOINTS["bridge"])

ethurl = "%s%s" % (ethhost, ENDPOINTS["bridge"])

historyurl = "%s%s" % (historyhost, ENDPOINTS["history"]) 

#emailurl = "%s%s" % (emailhost, ENDPOINTS["email"]) 
emailurl = "%s%s" % (emailhost, ENDPOINTS["email"])


DBNAME = "pmes"
ACCOUNTS = "accounts"
NEWS = "news"
WALLET = "wallet"
BALANCE = "balance"

QTUM = "QTUM"
ETH = "ETH"
OFFER = "offer"
CONTENT = "content"
REVIEW = "review"
DEAL = "deal"

AVAILABLE_COIN_ID = ["QTUM", "ETH"]

BILLING_FILE = "pdms/qtum_bridge/robin8_billing/qtum_billing"

bridges = {"ETH": ethurl, "QTUM": bridgeurl}

DEBUG = True

