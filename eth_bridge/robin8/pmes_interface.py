from abc import abstractmethod, ABCMeta


class Pmes_Interface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def setDescription(self, cid, descr):
        return NotImplementedError()

    @abstractmethod
    def getCid(self, ipfs_hash):
        return NotImplementedError()

    @abstractmethod
    def setAccessLevel(self, address, level):
        return NotImplementedError()

    @abstractmethod
    def publishersMap(self, address):
        return NotImplementedError()

    @abstractmethod
    def CidBuyerIdToOfferId(self, cid, buyer_address):
        return NotImplementedError()

    @abstractmethod
    def addReview(self, cid, address, review):
        return NotImplementedError()

    @abstractmethod
    def CidToOfferIds(self, cid, index):
        return NotImplementedError()

    @abstractmethod
    def nextOfferId(self):
        return NotImplementedError()

    @abstractmethod
    def makeOffer(self, cid, buyer_address, offer_type, offer_price, buyer_access_string):
        return NotImplementedError()

    @abstractmethod
    def sellContent(self, cid, buyer_address, seller_public_key, access_string):
        return NotImplementedError()

    @abstractmethod
    def offers(self, offer_id):
        return NotImplementedError()

    @abstractmethod
    def makeCid(self, data, address, descr, read_price, write_price):
        return NotImplementedError()

    @abstractmethod
    def owner(self):
        return NotImplementedError()

    @abstractmethod
    def setReadPrice(self, cid, price):
        return NotImplementedError()

    @abstractmethod
    def BuyerIdToOfferIds(self, buyer_address, index):
        return NotImplementedError()

    @abstractmethod
    def reviews(self, cid, index):
        return NotImplementedError()

    @abstractmethod
    def changeOwner(self, cid, new_owner, seller_public_key, access_string):
        return NotImplementedError()

    @abstractmethod
    def contents(self, cid):
        return NotImplementedError()

    @abstractmethod
    def getCus(self, cid):
        return NotImplementedError()

    @abstractmethod
    def getDescription(self, cid):
        return NotImplementedError()

    @abstractmethod
    def getOwner(self, cid):
        return NotImplementedError()

    @abstractmethod
    def getReadPrice(self, cid):
        return NotImplementedError()

    @abstractmethod
    def getWritePrice(self, cid):
        return NotImplementedError()

    @abstractmethod
    def setWritePrice(self, cid, price):
        return NotImplementedError()

    @abstractmethod
    def nextCid(self):
        return NotImplementedError()

    @abstractmethod
    def rejectOffer(self, cid, buyer_address):
        return NotImplementedError()



