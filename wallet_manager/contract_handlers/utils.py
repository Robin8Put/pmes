from bip32keys.bip32addresses import Bip32Addresses
import sha3
import json


def abi_to_func_hashes(abi):
    func_hashes = {}
    abi = json.loads(abi)

    for fn in abi:
        if 'name' not in fn:
            continue
        if fn['type'] != 'function':
            continue
        fn_sig = fn['name']
        fn_sig += '('
        for in_param in fn['inputs']:
            fn_sig += in_param['type']
            fn_sig += ','
        if fn_sig[-1] == ',':
            fn_sig = fn_sig[:-1] + ')'
        else:
            fn_sig = fn_sig + ')'
        k = sha3.keccak_256()
        k.update(fn_sig.encode())
        hash = k.hexdigest()[:8]
        func_hashes[fn['name']] = hash
    return func_hashes


if __name__ == '__main__':
    func_hashes = abi_to_func_hashes(
        '[{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"description","type":"string"}],"name":"setDescription","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"cus","type":"string"}],"name":"getCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"publisherAddress","type":"address"},{"name":"accessLevel","type":"uint256"}],"name":"setAccessLevel","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"publishersMap","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"address"}],"name":"CidBuyerIdToOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"review","type":"string"}],"name":"addReview","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"CidToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"nextOfferId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"},{"name":"buyerAccessString","type":"string"}],"name":"makeOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerAccessString","type":"string"}],"name":"sellContent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"offers","outputs":[{"name":"buyerAccessString","type":"string"},{"name":"sellerAccessString","type":"string"},{"name":"status","type":"uint8"},{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"offerType","type":"uint256"},{"name":"price","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cus","type":"string"},{"name":"ownerId","type":"address"},{"name":"description","type":"string"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"name":"makeCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setReadPrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"uint256"}],"name":"BuyerIdToOfferIds","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"name":"reviews","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"},{"name":"sellerAccessString","type":"string"}],"name":"changeOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"contents","outputs":[{"name":"cus","type":"string"},{"name":"description","type":"string"},{"name":"owner","type":"address"},{"name":"readPrice","type":"uint256"},{"name":"writePrice","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"price","type":"uint256"}],"name":"setWritePrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"nextCid","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"cid","type":"uint256"},{"name":"buyerId","type":"address"}],"name":"rejectOffer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')
    print(func_hashes)
