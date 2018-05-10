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
	"ams": r"/api/accounts/*",       
	#Get accounts data
	"account": r"/api/accounts/([a-zA-Z0-9]+?)/*",
	#Get/Post balance
	"balance": "/api/accounts/([a-zA-Z0-9]+?)/balance",
	#GRUD data with blockchain
	"blockchain_data": "/api/blockchain/data",    
	#Get last block id 
	"lastblockid": "/api/blockchain/lastblockid",
	#GRUD owner by cid
	"owner": "/api/blockchain/owner",
	#Get/POST content description
	"description": "/api/blockchain/description",
	#GRUD content description
	"access_string": "/api/blockchain/access_string",
	#Sale with blockchain
	"sale": "/api/blockchain/sale",
	#History server
	"history": "/api/history"
}

DBNAME = "pmes"
COLLECTION = "accounts"