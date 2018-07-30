from robin8.pmes_interface import Pmes_Interface
from robin8.eth_contract_handler import EthContractHandler


class PmesEthContractHandler(Pmes_Interface, EthContractHandler):


    def setDescription(self, cid, description):
        return self.send_to_contract(self.contract.functions.setDescription(cid, description))

    def getCid(self, ipfs_hash):
        return self.contract.functions.getCid(ipfs_hash).call()

    def setAccessLevel(self, address, level):
        return self.send_to_contract(self.contract.functions.setAccessLevel(address, level))

    def publishersMap(self, address):
        return self.contract.functions.publishersMap(address).call()

    def CidBuyerIdToOfferId(self, cid, buyer_address):
        return self.contract.functions.CidBuyerIdToOfferId(cid, buyer_address).call()

    def addReview(self, cid, address, review):
        return self.send_to_contract(self.contract.functions.addReview(cid, address, review))

    def CidToOfferIds(self, cid, index):
        return self.contract.functions.CidToOfferIds(cid, index).call()

    def nextOfferId(self):
        return self.contract.functions.nextOfferId().call()

    def makeOffer(self, cid, buyer_address, offer_type, offer_price, buyer_access_string):
        return self.send_to_contract(self.contract.functions.makeOffer(cid, buyer_address, offer_type, offer_price, buyer_access_string))

    def sellContent(self, cid, buyer_address, seller_public_key, access_string):
        return self.send_to_contract(self.contract.functions.sellContent(cid, buyer_address, seller_public_key, access_string))

    def offers(self, offer_id):
        res = self.contract.functions.offers(offer_id).call()
        return {'buyer_access_string': res[0], 'seller_public_key': res[1], 'seller_access_string': res[2], 'status': res[3], 'cid': res[4], 'buyer_address': res[5][2:], 'type': res[6], 'price': res[7]}


    def makeCid(self, data, address, descr, read_price, write_price):
        return self.send_to_contract(self.contract.functions.makeCid(data, address, descr, read_price, write_price))

    def owner(self):
        return self.contract.functions.owner().call()[2:]

    def setReadPrice(self, cid, price):
        return self.send_to_contract(self.contract.functions.setReadPrice(cid, price))

    def BuyerIdToOfferIds(self, buyer_address, index):
        return self.contract.functions.BuyerIdToOfferIds(buyer_address, index).call()

    def reviews(self, cid, index):
        return self.contract.functions.reviews(cid, index).call()

    def changeOwner(self, cid, new_owner, seller_public_key, access_string):
        return self.send_to_contract(self.contract.functions.changeOwner(cid, new_owner, seller_public_key, access_string))

    def contents(self, cid):
        res = self.contract.functions.contents(cid).call()
        return {'cus': res[0], 'description': res[1], 'owner': res[2][2:], 'read_price': res[3], 'write_price': res[4]}

    def getCus(self, cid):
        return self.contents(cid)['cus']

    def getDescription(self, cid):
        return self.contents(cid)['description']

    def getOwner(self, cid):
        return self.contents(cid)['owner']

    def getReadPrice(self, cid):
        return self.contents(cid)['read_price']

    def getWritePrice(self, cid):
        return self.contents(cid)['write_price']

    def setWritePrice(self, cid, price):
        return self.send_to_contract(self.contract.functions.setWritePrice(cid, price))

    def nextCid(self):
        return self.contract.functions.nextCid().call()

    def rejectOffer(self, cid, buyer_address):
        return self.send_to_contract(self.contract.functions.rejectOffer(cid, buyer_address))

    def get_cid_offers(self, cid):
        res = []
        index = 0
        try:
            while True:
                offer_id = self.CidToOfferIds(cid, index)
                if offer_id == 0:
                    break
                res.append(self.offers(offer_id))
                index += 1
        except:
            pass
        return res

    def get_buyer_offers(self, buyer_address):
        res = []
        index = 0
        try:
            while True:
                offer_id = self.BuyerIdToOfferIds(buyer_address, index)
                if offer_id == 0:
                    break
                res.append(self.offers(offer_id))
                index += 1
        except:
            pass
        return res

    def get_reviews(self, cid):
        res = []
        index = 0
        try:
            while True:
                review = self.reviews(cid, index)
                res.append(review)
                index += 1
        except:
            pass
        return res

if __name__ == '__main__':
    handler = PmesEthContractHandler.from_http_provider('https://rinkeby.infura.io/jPgsGcw3RjKP5MjlcJeg', '0xE4294fA1692e6B69781064594a14982480Ed44bb', '[{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"description","type":"string"}],"name":"setDescription","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"cus","type":"string"}],"name":"getCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"publisherAddress","type":"address"},{"name":"accessLevel","type":"uint256"}],"name":"setAccessLevel","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"publishersMap","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"address"}],"name":"CidBuyerIdToOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"review","type":"string"}],"name":"addReview","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"CidToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"nextOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"},{"name":"buyerAccessString","type":"string"}],"name":"makeOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerAccessString","type":"string"}],"name":"sellContent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"offers","outputs":[{"name":"buyerAccessString","type":"string"},{"name":"sellerAccessString","type":"string"},{"name":"status","type":"uint8"},{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cus","type":"string"},{"name":"ownerId","type":"address"},{"name":"description","type":"string"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"name":"makeCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setReadPrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"uint256"}],"name":"BuyerIdToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"reviews","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerAccessString","type":"string"}],"name":"changeOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"contents","outputs":[{"name":"cus","type":"string"},{"name":"description","type":"string"},{"name":"owner","type":"address"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setWritePrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"nextCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"}],"name":"rejectOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')
    handler.set_send_params({'private_key': '89b255e8b0ff38b033bb45202c2eb3d66b9044e5a4e5a290f1fdcded930abb35'})
    #print(handler.makeCid("amaizing", "0xdD870fA1b7C4700F2BD7f44238821C26f7392148", "descr", 100, 100))
    print(handler.contents(2))
    print(handler.getCus(1))
    print(handler.owner())
    #print(handler.makeOffer(2, "0x14723A09ACff6D2A60DcdF7aA4AFf308FDDC160C", 1, 5, "test"))
    print(handler.nextCid())
    print(handler.nextOfferId())
    print(handler.CidToOfferIds(2, 0))
    print(handler.offers(1))
    print(handler.BuyerIdToOfferIds('0x14723A09ACff6D2A60DcdF7aA4AFf308FDDC160C', 0))
    #print(handler.sellContent(2, "0x14723A09ACff6D2A60DcdF7aA4AFf308FDDC160C", "test"))
    #print(handler.addReview(2, "0x14723A09ACff6D2A60DcdF7aA4AFf308FDDC160C", "my awesome review"))
    print(handler.reviews(2, 0))

    print(handler.get_reviews(2))
    print(handler.get_cid_offers(2))
    print(handler.get_buyer_offers('0x14723A09ACff6D2A60DcdF7aA4AFf308FDDC160C'))