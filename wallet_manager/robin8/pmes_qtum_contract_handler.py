from robin8.qtum_contract_handler import QtumContractHandler
from robin8.pmes_interface import Pmes_Interface


class PmesQtumContractHandler(Pmes_Interface, QtumContractHandler):

    def setDescription(self, cid, descr):
        return self.send_to_contract(func_name='setDescription', input_types=['uint256', 'string'],
                                     input_values=[cid, descr], output_types=None)

    def getCid(self, ipfs_hash):
        return self.call_contract(func_name='getCid', input_types=['string'],
                                  input_values=[ipfs_hash], output_types=['uint256'])[0]

    def setAccessLevel(self, address, level):
        return self.send_to_contract(func_name='setAccessLevel', input_types=['address', 'uint256'],
                                     input_values=[address, level], output_types=None)

    def publishersMap(self, address):
        return self.call_contract(func_name='publishersMap', input_types=['address'],
                                  input_values=[address], output_types=['uint256'])[0]

    def CidBuyerIdToOfferId(self, cid, buyer_address):
        return self.call_contract(func_name='CidBuyerIdToOfferId', input_types=['uint256', 'address'],
                                  input_values=[cid, buyer_address], output_types=['uint256'])[0]

    def addReview(self, cid, address, review):
        return self.send_to_contract(func_name='addReview', input_types=['uint256', 'address', 'string'],
                                     input_values=[cid, address, review], output_types=None)

    def CidToOfferIds(self, cid, index):
        return self.call_contract(func_name='CidToOfferIds', input_types=['uint256', 'uint256'],
                                  input_values=[cid, index], output_types=['uint256'])[0]

    def nextOfferId(self):
        return self.call_contract(func_name='nextOfferId', input_types=None,
                                  input_values=None, output_types=['uint256'])[0]

    def makeOffer(self, cid, buyer_address, offer_type, offer_price, buyer_access_string):
        return self.send_to_contract(func_name='makeOffer', input_types=['uint256', 'address', 'uint256', 'uint256', 'string'],
                                     input_values=[cid, buyer_address, offer_type, offer_price, buyer_access_string], output_types=None)

    def sellContent(self, cid, buyer_address, seller_public_key, access_string):
        return self.send_to_contract(func_name='sellContent', input_types=['uint256', 'address', 'string', 'string'],
                                     input_values=[cid, buyer_address, seller_public_key, access_string], output_types=None)

    def offers(self, offer_id):
        res = self.call_contract(func_name='offers', input_types=['uint256'],
                                  input_values=[offer_id],
                                  output_types=['string', 'string', 'string', 'uint8', 'uint256', 'address', 'uint256', 'uint256'])
        return {'buyer_access_string': res[0].decode(), 'seller_public_key': res[1].decode(), 'seller_access_string': res[2].decode(), 'status': res[3], 'cid': res[4], 'buyer_address': res[5][2:], 'type': res[6], 'price': res[7]}

    def makeCid(self, data, address, descr, read_price, write_price):
        return self.send_to_contract(func_name='makeCid', input_types=['string', 'address', 'string', 'uint256', 'uint256'],
                                     input_values=[data, address, descr, read_price, write_price], output_types=None)

    def owner(self):
        return self.call_contract(func_name='owner', input_types=None,
                                  input_values=None, output_types=['address'])[0]

    def setReadPrice(self, cid, price):
        return self.send_to_contract(func_name='setReadPrice', input_types=['uint256', 'uint256'],
                                     input_values=[cid, price], output_types=None)

    def BuyerIdToOfferIds(self, buyer_address, index):
        return self.call_contract(func_name='BuyerIdToOfferIds', input_types=['address', 'uint256'],
                                  input_values=[buyer_address, index], output_types=['uint256'])[0]

    def reviews(self, cid, index):
        return self.call_contract(func_name='reviews', input_types=['uint256', 'uint256'],
                                  input_values=[cid, index], output_types=['string'])[0].decode()

    def changeOwner(self, cid, new_owner, seller_public_key, access_string):
        return self.send_to_contract(func_name='changeOwner', input_types=['uint256', 'address', 'string', 'string'],
                                     input_values=[cid, new_owner, seller_public_key, access_string], output_types=None)

    def contents(self, cid):
        res = self.call_contract(func_name='contents', input_types=['uint256'],
                                  input_values=[cid], output_types=['string', 'string', 'address', 'uint256', 'uint256'])
        return {'cus': res[0].decode(), 'description': res[1].decode(), 'owner': res[2][2:], 'read_price': res[3], 'write_price': res[4]}

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
        return self.send_to_contract(func_name='setWritePrice', input_types=['uint256', 'uint256'],
                                     input_values=[cid, price], output_types=None)

    def nextCid(self):
        return self.call_contract(func_name='nextCid', input_types=[],
                                  input_values=[], output_types=['uint256'])[0]

    def rejectOffer(self, cid, buyer_address):
        return self.send_to_contract(func_name='rejectOffer', input_types=['uint256', 'address'],
                                     input_values=[cid, buyer_address], output_types=None)

    def get_cid_offers(self, cid):
        res = []
        index = 0
        try:
            while True:
                offer_id = self.CidToOfferIds(cid, index)
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
    handler = PmesQtumContractHandler.from_http_provider('http://qtumuser:qtum2018@127.0.0.1:8333', '9246b129bcbed0f5e6cdb46a20b8ee7b9105a131',
                                                         '[{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"description","type":"string"}],"name":"setDescription","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"cus","type":"string"}],"name":"getCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"publisherAddress","type":"address"},{"name":"accessLevel","type":"uint256"}],"name":"setAccessLevel","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"publishersMap","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"address"}],"name":"CidBuyerIdToOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"review","type":"string"}],"name":"addReview","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"CidToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"nextOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"},{"name":"buyerAccessString","type":"string"}],"name":"makeOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerAccessString","type":"string"}],"name":"sellContent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"offers","outputs":[{"name":"buyerAccessString","type":"string"},{"name":"sellerAccessString","type":"string"},{"name":"status","type":"uint8"},{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cus","type":"string"},{"name":"ownerId","type":"address"},{"name":"description","type":"string"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"name":"makeCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setReadPrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"uint256"}],"name":"BuyerIdToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"reviews","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerAccessString","type":"string"}],"name":"changeOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"contents","outputs":[{"name":"cus","type":"string"},{"name":"description","type":"string"},{"name":"owner","type":"address"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setWritePrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"nextCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"}],"name":"rejectOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')
    handler.set_send_params({'sender': 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'})
    #handler.makeCid("amaizing", "0xdd870fa1b7c4700f2bd7f44238821c26f7392148", "descr", 100, 100)
    print(handler.nextCid())
    #handler.makeOffer(2, "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c", 1, 5, "test")
    print(handler.nextOfferId())
    print(handler.owner())
    print(handler.getCid('test'))
    print(handler.publishersMap('0xfdc1ae05c161833cdf135863e332126e15d7568c'))
    print(handler.CidBuyerIdToOfferId(1, "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c"))
    print(handler.CidToOfferIds(1, 0))
    print(handler.offers((1)))
    print(handler.BuyerIdToOfferIds("0x14723a09acff6d2a60dcdf7aa4aff308fddc160c", 0))
    print(handler.contents(1))
    #print(handler.sellContent(1, "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c", "test"))
    #print(handler.addReview(1, "0x14723a09acff6d2a60dcdf7aa4aff308fddc160c", "my awesome review"))
    print(handler.reviews(1, 0))
    print(handler.getDescription(1))
    print(handler.getWritePrice(1))
    print(handler.getOwner(6))

    print(handler.get_reviews(1))
    print(handler.get_cid_offers(1))
    print(handler.get_buyer_offers('0x14723a09acff6d2a60dcdf7aa4aff308fddc160c'))




