from robin8.Qtum_SC import Qtum_SC
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import ipfsapi
from R8_IPFS import R8_IPFS
import time

contract_owner = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'
contract_owner_hex = 'fdc1ae05c161833cdf135863e332126e15d7568c'
contract_address = '35ed993779a476a5993f3190805c409fca1c72ed'


class Robin8_SC(Qtum_SC):

    def __init__(self, contract_address, qtum_rpc=None):
        func_hashes = {
            'CIDtoDescription': "12df1c63",  # "CIDtoDescription(uint32)"
            'changeOwner': "b16e7883",  # changeOwner(uint32,address,string)
            'getCID': "1c461ee1",  # "getCID(string)",
            'getCUS': "d5b4bb60",  # "getCUS(uint32)",
            'getOwner': "621b23e2",  # "getOwner(uint32)",
            'lastAccessString': "3d2ecd6f",  #  lastAccessString(uint32)
            'makeCID': "cc16dffe",  # "makeCID(string,address)",
            'publishersMap': "3a8c50b9",  # "publishersMap(address)",
            'sellContent': "cdf359ba",  #  sellContent(uint32,address,string)
            'setAccessLevel': "da4d934a",  #: "setAccessLevel(address,uint8)",
            'setCIDdescription': "ab63c0ed",  # "setCIDdescription(uint32,string)"
        }
        super().__init__(contract_address, func_hashes, qtum_rpc)

    def CIDtoDescription(self, cid):
        return self.callcontract(func_name='CIDtoDescription', input_types=['uint32'], input_values=[cid], output_types=['string'])

    def changeOwner(self, cid, new_owner, access_string):
        return self.sendtocontract(func_name='changeOwner', input_types=['uint32', 'address', 'string'], input_values=[cid, new_owner, access_string], output_types=None)

    def getCID(self, ipfs_hash):
        return self.callcontract(func_name='getCID', input_types=['string'], input_values=[ipfs_hash], output_types=['uint32'])

    def getCUS(self, cid):
        return self.callcontract(func_name='getCUS', input_types=['uint32'], input_values=[cid], output_types=['string'])

    def getOwner(self, cid):
        return self.callcontract(func_name='getOwner', input_types=['uint32'], input_values=[cid], output_types=['address'])

    def lastAccessString(self, cid):
        return self.callcontract(func_name='lastAccessString', input_types=['uint32'], input_values=[cid], output_types=['string'])

    def publishersMap(self, address):
        return self.callcontract(func_name='publishersMap', input_types=['address'], input_values=[address], output_types=['string'])

    def makeCID(self, data, address):
        return self.sendtocontract(func_name='makeCID', input_types=['string', 'address'], input_values=[data, address], output_types=['uint32'])

    def sellContent(self, cid, buyer_addr, access_string):
        return self.sendtocontract(func_name='changeOwner', input_types=['uint32', 'address', 'string'], input_values=[cid, buyer_addr, access_string], output_types=None)

    def setAccessLevel(self, address, level):
        return self.sendtocontract(func_name='setAccessLevel', input_types=['address', 'level'], input_values=[address, level], output_types=None)

    def setCIDdescription(self, cid, desc):
        return self.sendtocontract(func_name='setCIDdescription', input_types=['uint32', 'string'], input_values=[cid, desc], output_types=None)



def create_cid(content):
    r8_ipfs = R8_IPFS()
    ipfs_hash = r8_ipfs.upload_to_ipfs(content)

    r8_sc = Robin8_SC(contract_address)

    r8_sc.set_send_params({'sender': contract_owner})

    print(r8_sc.makeCID(ipfs_hash, contract_owner_hex))
    return ipfs_hash



if __name__=='__main__':
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})
    r8_ipfs = R8_IPFS()
    print(R8_IPFS.encode_sc('Hello world'))
    # data = 'Encrypted user data'
    # print('data: ', data)
    #
    # ipfs_hash = create_cid('Encrypted user data')
    # print('ipfs_hash: ', ipfs_hash)
    #
    # time.sleep(300)
    ipfs_hash = 'QmZApo2gvUPRaG1DHFagFJGwTqvTZ68LAgjhVWRcniHDXD'

    cid = int(r8_sc.getCID(ipfs_hash)[0])
    print('cid: ', cid)

    # desc = 'This is the desc for my enc data'
    # print('desc: ', desc)
    # print(r8_sc.setCIDdescription(cid, desc))
    #
    # time.sleep(60)

    cus = r8_sc.getCUS(cid)[0]
    print('cus: ', cus)

    content = r8_ipfs[ipfs_hash]
    print('downloaded content: ', content)

    desc = r8_sc.CIDtoDescription(cid)
    print('downloaded desc: ', desc)
