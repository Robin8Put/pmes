from robin8.qtum_sc import Qtum_SC


class Robin8_SC(Qtum_SC):

    def __init__(self, contract_address, qtum_rpc=None):
        func_hashes = {
            'CIDtoDescription': "12df1c63",  # "CIDtoDescription(uint32)"
            'addReview': "e61a8fec",         # (address, uint32, string)
            'changeOwner': "b16e7883",  # changeOwner(uint32,address,string)
            'getCID': "1c461ee1",  # "getCID(string)",
            'getCUS': "d5b4bb60",  # "getCUS(uint32)",
            'getOwner': "621b23e2",  # "getOwner(uint32)",
            'getReadPrice': "3db6dbce",
            'getWritePrice': "2ec215dc",
            'lastAccessString': "3d2ecd6f",  #  lastAccessString(uint32)
            'makeCID': "e9d9bd60",  # "makeCID(string,address,string,uint)",
            'makeOffer': "e549b34a",  # makeOffer(uint32,address,uint256,string)
            'rejectOffer': "619cc363",  # rejectOffer(uint32,address)
            'publishersMap': "3a8c50b9",  # "publishersMap(address)",
            'sellContent': "cdf359ba",  #  sellContent(uint32,address,string)
            'setAccessLevel': "da4d934a",  #: "setAccessLevel(address,uint8)",
            'setCIDdescription': "ab63c0ed",  # "setCIDdescription(uint32,string)"
            'setReadPrice': "c96884cb",
            'setWritePrice': "bd1f9091",
        }
        super().__init__(contract_address, func_hashes, qtum_rpc)

    def CIDtoDescription(self, cid):
        return self.callcontract(func_name='CIDtoDescription', input_types=['uint32'],
                                 input_values=[cid], output_types=['string'])

    def changeOwner(self, cid, new_owner, access_string):
        return self.sendtocontract(func_name='changeOwner', input_types=['uint32', 'address', 'string'],
                                   input_values=[cid, new_owner, access_string], output_types=None)

    def getCID(self, ipfs_hash):
        return self.callcontract(func_name='getCID', input_types=['string'],
                                 input_values=[ipfs_hash], output_types=['uint32'])

    def getCUS(self, cid):
        return self.callcontract(func_name='getCUS', input_types=['uint32'],
                                 input_values=[cid], output_types=['string'])

    def getOwner(self, cid):
        return self.callcontract(func_name='getOwner', input_types=['uint32'],
                                 input_values=[cid], output_types=['address'])

    def getReadPrice(self, cid):
        return self.callcontract(func_name='getReadPrice', input_types=['uint32'],
                                 input_values=[cid], output_types=['uint'])

    def getWritePrice(self, cid):
        return self.callcontract(func_name='getWritePrice', input_types=['uint32'],
                                 input_values=[cid], output_types=['uint'])

    def lastAccessString(self, cid):
        return self.callcontract(func_name='lastAccessString', input_types=['uint32'],
                                 input_values=[cid], output_types=['string'])

    def publishersMap(self, address):
        return self.callcontract(func_name='publishersMap', input_types=['address'],
                                 input_values=[address],
                                 output_types=['string'])

    def makeCID(self, data, address, descr, read_price, write_price):
        return self.sendtocontract(func_name='makeCID', input_types=['string', 'address', 'string', 'uint', 'uint'],
                                   input_values=[data, address, descr, read_price, write_price], output_types=['uint32'])

    def sellContent(self, cid, buyer_addr, access_string):
        return self.sendtocontract(func_name='changeOwner', input_types=['uint32', 'address', 'string'],
                                   input_values=[cid, buyer_addr, access_string], output_types=None)

    def setAccessLevel(self, address, level):
        return self.sendtocontract(func_name='setAccessLevel', input_types=['address', 'level'],
                                   input_values=[address, level], output_types=None)

    def setCIDdescription(self, cid, desc):
        return self.sendtocontract(func_name='setCIDdescription', input_types=['uint32', 'string'],
                                   input_values=[cid, desc], output_types=None)

    def makeOffer(self, cid, buyer_addr, offer_type, offer_price, buyer_access_string):
        return self.sendtocontract(func_name='makeOffer', input_types=['uint32', 'address', 'uint8', 'uint', 'string'],
                                   input_values=[cid, buyer_addr, offer_type, offer_price, buyer_access_string], output_types=None)

    def rejectOffer(self, cid, buyer_addr):
        return self.sendtocontract(func_name="rejectOffer", input_types=['uint32', 'address'],
                                   input_values=[cid, buyer_addr], output_types=None)

    def setReadPrice(self, cid, price):
        return self.sendtocontract(func_name="setReadPrice", input_types=['uint32', 'uint'],
                                   input_values=[cid, price], output_types=None)

    def setWritePrice(self, cid, price):
        return self.sendtocontract(func_name="setWritePrice", input_types=['uint32', 'uint'],
                                   input_values=[cid, price], output_types=None)

    def addReview(self, address, cid, review):
        return self.sendtocontract(func_name="addReview", input_types=['string', 'uint32', 'string'],
                                   input_values=[address, cid, review], output_types=None)
