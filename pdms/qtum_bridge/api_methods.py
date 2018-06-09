# todo: handle invalid params

from jsonrpcserver.aio import methods
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from R8_IPFS import R8_IPFS
from robin8.Robin8_SC import Qtum_SC, Robin8_SC
from R8_Balance import R8_Balance
from hashlib import sha256
from qtum_blockchain.qtum_blockchain import Qtum_Blockchain
from robin8_billing import robin8_billing
import logging
import json
import os
import settings
from jsonrpcclient.http_client import HTTPClient
from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import RobustTornadoClient, SignedTornadoClient 

contract_owner = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'
contract_owner_hex = 'fdc1ae05c161833cdf135863e332126e15d7568c'
contract_address = '52b81892235027453bcdbc2ec25ec7253c531efc'
decimals = 8


api_pass = 'AP'

billing = robin8_billing.Robin8_Billig("pmes/pdms/qtum_bridge/robin8_billing/billing")
client_storage = RobustTornadoClient(settings.storageurl)
client_balance = SignedTornadoClient(settings.balanceurl)


def verify(func):
    async def wrapper(*args, **kwargs):
        import settings
        with open(os.path.join(settings.BASE_DIR, "keys.json")) as f:
            keys = json.load(f)

        pubkey = keys["pubkey"]

        message = kwargs.get("message")
        signature = kwargs.get("signature")
        try:
            flag = Qtum.verify_message(message, signature, pubkey)
        except:
            flag = None
        if not flag:
            result =  {"error":403, "reason":"Invalid signature"}
        else:
            result = await func(*args, **kwargs)
        return result
    return wrapper


def init_qtum():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018"))
    return rpc_connection


def double_sha256(str):
    return sha256(sha256(str).digest()).hexdigest()


def verify_secret(*params, secret):
    str = ''
    for p in params:
        str += p
    str = str.encode()
    return double_sha256(str) == secret


@methods.add
async def test():
    return 'It works'


@methods.add
async def post_test(car):
    return 'Your car is %s' % car


@methods.add
async def lastblockid():
    res = Qtum_Blockchain(init_qtum()).get_lastblockid()
    return res


@methods.add
async def balance():
    qtum = init_qtum()
    unspent = qtum.listunspent()
    addr_arr = {}
    total_sum = 0
    for tx in unspent:
        addr = tx['address']
        amount = tx['amount']
        if addr in addr_arr:
            addr_arr[addr] += float(amount)
        else:
            addr_arr[addr] = float(amount)
        total_sum += float(amount)

    addr_arr['total'] = float(total_sum)
    addr_arr['getbl'] = float(qtum.getbalance())

    encoded_arr = {k: R8_Balance(v, decimals).get_balance() for k, v in addr_arr.items()}
    encoded_arr['decimals'] = decimals
    return encoded_arr


@methods.add
async def ipfscat(hash):
    ipfs = R8_IPFS()
    ipfs_data = ipfs.download_from_ipfs(hash).decode()
    print(ipfs.download_from_ipfs(hash))
    if not ipfs_data:
        version = ipfs.version()
        if not version:
            return {"data": None}
        else:
            return {"data": None, "code": 404}

    return {"data":ipfs_data}


@methods.add
async def getcid(hash):

    r8_sc = Robin8_SC(contract_address)
    cid = r8_sc.getCID(hash)[0]
    if cid == 0:
        return {'cid': None}

    return {"cid":str(cid)}


@methods.add
async def readbycid(cid):
    robin8 = Robin8_SC(contract_address)
    cus = robin8.getCUS(cid)[0].decode()

    if not cus:
        return {'content':None, 'code': 404}
    if cus[0:2] == 'Qm' and len(cus) > 30:
        return await ipfscat(cus)
    return {"content":cus}


@methods.add
async def ownerbycid(cid):
    cid = int(cid)
    r8_sc = Robin8_SC(contract_address)

    owner_hex_addr = r8_sc.getOwner(cid)[0]
    if not owner_hex_addr:
        return {'owneraddr': None, 'code': 404}
    owner_hex_addr = owner_hex_addr[2:]  # remove 0x
    if owner_hex_addr.replace('0', '') == '':
        return {'owneraddr': None, 'code': 404}
    qtum = init_qtum()

    owneraddr = qtum.fromhexaddress(owner_hex_addr)

    return {"owneraddr":owner_hex_addr}


@methods.add
async def descrbycid(cid):
    r8_sc = Robin8_SC(contract_address)

    descr = r8_sc.CIDtoDescription(cid)[0].decode()
    if not descr:
        return {'description': None, 'code': 404}

    if descr[0:2] == 'Qm' and len(descr) > 30:
        return await ipfscat(descr)

    return {"description":descr}


@methods.add
async def makecid(cus, owneraddr, description, price): #addr, blockid, secret):

    content_fee = billing.estimate_upload_fee(len(cus))

    descr_fee = billing.estimate_set_descr_fee(len(description))

    user = await client_storage.request(method_name="getaccountbywallet", 
                                wallet=owneraddr)
    if "error" in user.keys():
        return user

    balance = await client_balance.request(method_name="getbalance", uid=user["id"])

    if "error" in balance.keys():
        return balance

    common_price = int(content_fee) + int(descr_fee)

    diff = int(list(balance.values())[0]) - common_price

    if diff < 0:
        return {"error":403, "reason": "Balance is not enough."}

    decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                            amount=common_price)

    if "error" in decbalance.keys():
        return decbalance
    
    addr = contract_owner
    # blockid = await lastblockid()
    # if not verify_secret(api_pass, blockid, addr, owneraddr, cus, secret=secret):
    #     return {'error': 'Bad secret'}
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': addr})
    qtum = init_qtum()
    r8_ipfs = R8_IPFS()

    ipfs_hash = r8_ipfs.upload_to_ipfs(cus)
    descr_hash = r8_ipfs.upload_to_ipfs(description)

    cid = r8_sc.getCID(ipfs_hash)[0]
    if cid != 0:
        return {'error': 'file was uploaded'}
    logging.debug("Before result")
    result = r8_sc.makeCID(ipfs_hash, owneraddr, descr_hash, price)

    return {'result': result, 'hash': ipfs_hash, 'cus': cus, 'addr': addr, 'owner_hex_addr': owneraddr}#, 'blockid': blockid, 'secret': secret}


@methods.add
async def setdescrforcid(cid, descr, owneraddr):#, addr, blockid, secret):
    user = await client_storage.request(method_name="getaccountbywallet", 
                                wallet=owneraddr)
    if "error" in user.keys():
        return user

    balance = await client_balance.request(method_name="getbalance", uid=user["id"])

    if "error" in balance.keys():
        return balance

    fee = billing.estimate_set_descr_fee(len(descr))
    

    if int(balance[str(user["id"])]) - int(fee) < 0:
        return {"error":403, "reason":"Owner does not have enough balance."}

    decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                amount=fee)

    if "error" in decbalance.keys():
        return decbalance

    addr = contract_owner
    # blockid = await lastblockid()
    # if not verify_secret(api_pass, blockid, addr, cid, descr, secret=secret):
    #     return {'error': 'Bad secret'}
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': addr})
    ipfs = R8_IPFS()

    ipfs_hash = ipfs.upload_to_ipfs(descr)

    result = r8_sc.setCIDdescription(cid, ipfs_hash)

    return {'result': result, 'cid': str(cid), 'descr': descr, 'addr': addr}  # 'secret': secret, 'blockid': blockid}


@methods.add
async def last_access_string(cid):
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})

    result = r8_sc.lastAccessString(cid)[0].decode()
    print(result)

    return result


@methods.add
async def changeowner(cid, new_owner, access_string):

    user = await client_storage.request(method_name="getaccountbywallet", 
                                            wallet=new_owner)
    if "error" in user.keys():
        return user

    balance = await client_balance.request(method_name="getbalance", 
                                            uid=user["id"])

    if "error" in balance.keys():
        return balance

    fee = billing.estimate_change_owner_fee()
    
    if int(list(balance.values())[0]) - int(fee) < 0:
        return {"error":403, "reason":"New owner does not have enough balance."}

    decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                amount=fee)

    if "error" in decbalance.keys():
        return decbalance

    addr = contract_owner_hex
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})

    qtum = init_qtum()

    result = r8_sc.changeOwner(cid, new_owner, access_string)
    prev_owner_hex = r8_sc.getOwner(cid)[0][2:]
    prev_owner = qtum.fromhexaddress(prev_owner_hex)

    

    return {'result': result, 'cid': str(cid), 'new_owner': new_owner, 'access_string': access_string, 'prev_owner': prev_owner, 'contract_owner_hex': addr}


@methods.add
async def sellcontent(cid, buyer_address, access_string):

    user = await client_storage.request(method_name="getaccountbywallet", 
                                wallet=buyer_address)
    if "error" in user.keys():
        return user

    balance = await client_balance.request(method_name="getbalance", uid=user["id"])

    if "error" in balance.keys():
        return balance

    fee = billing.estimate_sale_fee()
    
    if int(list(balance.values())[0]) - int(fee) < 0:
        return {"error":403, "reason": "Balance is not enough."}

    decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                amount=fee)

    if "error" in decbalance.keys():
        return decbalance

    addr = contract_owner
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})

    qtum = init_qtum()
    content_owner_hex = r8_sc.getOwner(cid)[0][2:]
    content_owner_addr = qtum.fromhexaddress(content_owner_hex)

    result = r8_sc.sellContent(cid, buyer_address, access_string)

   
    return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address, 'access_string': access_string, 'content_owner': content_owner_addr, 'contract_owner_hex': addr}


@methods.add
async def setprice(cid, price, owneraddr):
    fee = billing.estimate_set_price_fee()

    user = await client_storage.request(method_name="getaccountbywallet", 
                                wallet=owneraddr)
    if "error" in user.keys():
        return user

    balance = await client_balance.request(method_name="getbalance", uid=user["id"])

    if "error" in balance.keys():
        return balance

    if balance[str(user["id"])] == "Not found":
        return {"error":404, "reason":"User not found in balance"}

    decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                amount=fee)

    if "error" in decbalance.keys():
        return decbalance

    if int(balance[str(user["id"])]) - int(fee) < 0:
        return {"error":403, "reason": "Balance is not enough."}

    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})



    result = r8_sc.setPrice(cid, price)

    return {'result': result, 'cid': str(cid), 'price': price}


@methods.add
async def getprice(cid):
    r8_sc = Robin8_SC(contract_address)

    return r8_sc.getPrice(cid)[0]


@methods.add
async def make_offer(cid, buyer_address, price, buyer_access_string):

    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})
    logging.debug("Start result")
    result = r8_sc.makeOffer(cid, buyer_address, price, buyer_access_string)

    return {'result': result, 'cid': str(cid), 'offer_price': price,
            'buyer_address': buyer_address, 'buyer_access_string': buyer_access_string}


@methods.add
async def reject_offer(cid, buyer_address):
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})

    result = r8_sc.rejectOffer(cid, buyer_address)

    return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address}

"""

class Bridge(object):

    #@verify
    async def lastblockid(*args, **kwargs):
        res = Qtum_Blockchain(init_qtum()).get_lastblockid()
        return res


    #@verify
    async def balance(*args, **kwargs):
        qtum = init_qtum()
        unspent = qtum.listunspent()
        addr_arr = {}
        total_sum = 0
        for tx in unspent:
            addr = tx['address']
            amount = tx['amount']
            if addr in addr_arr:
                addr_arr[addr] += float(amount)
            else:
                addr_arr[addr] = float(amount)
            total_sum += float(amount)

        addr_arr['total'] = float(total_sum)
        addr_arr['getbl'] = float(qtum.getbalance())

        encoded_arr = {k: R8_Balance(v, decimals).get_balance() for k, v in addr_arr.items()}
        encoded_arr['decimals'] = decimals
        return encoded_arr


    #@verify
    async def ipfscat(*args, **kwargs):
        message = json.loads(kwargs["message"])
        hash = message.get("hash")
        ipfs = R8_IPFS()
        ipfs_data = ipfs.download_from_ipfs(hash).decode()
        print(ipfs.download_from_ipfs(hash))
        if not ipfs_data:
            version = ipfs.version()
            if not version:
                return {"data": None}
            else:
                return {"data": None, "code": 404}

        return {"data":ipfs_data}


    #@verify
    async def getcid(*args, **kwargs):
        message = json.loads(kwargs["message"])
        hash = message.get("hash")
        r8_sc = Robin8_SC(contract_address)
        cid = r8_sc.getCID(hash)[0]
        if cid == 0:
            return {'cid': None}

        return {"cid":str(cid)}


    #@verify
    async def readbycid(*args, **kwargs):
        message = json.loads(kwargs["message"])
        cid = int(message.get("cid", 0))
        robin8 = Robin8_SC(contract_address)
        cus = robin8.getCUS(cid)[0].decode()

        if not cus:
            return {'content':None, 'code': 404}
        if cus[0:2] == 'Qm' and len(cus) > 30:
            return await ipfscat(cus)
        return {"content":cus}


    #@verify
    async def ownerbycid(*args, **kwargs):
        message = json.loads(kwargs["message"])
        cid = int(message.get("cid", 0))
        r8_sc = Robin8_SC(contract_address)

        owner_hex_addr = r8_sc.getOwner(cid)[0]
        if not owner_hex_addr:
            return {'owneraddr': None, 'code': 404}
        owner_hex_addr = owner_hex_addr[2:]  # remove 0x
        if owner_hex_addr.replace('0', '') == '':
            return {'owneraddr': None, 'code': 404}
        qtum = init_qtum()

        owneraddr = qtum.fromhexaddress(owner_hex_addr)

        return {"owneraddr":owner_hex_addr}


    #@verify
    async def descrbycid(*args, **kwargs):
        message = json.loads(kwargs["message"])
        cid = int(message.get("cid", 0))
        r8_sc = Robin8_SC(contract_address)

        descr = r8_sc.CIDtoDescription(cid)[0].decode()
        if not descr:
            return {'description': None, 'code': 404}

        if descr[0:2] == 'Qm' and len(descr) > 30:
            return await ipfscat(descr)

        return {"description":descr}


    #@verify
    async def makecid(*args, **kwargs):
        message = json.loads(kwargs["message"])
        
        cus = message.get("cus")
        owneraddr = message.get("owneraddr")
        description = message.get("description")
        price = int(message.get("price", 0))

        content_fee = billing.estimate_upload_fee(len(cus))

        descr_fee = billing.estimate_set_descr_fee(len(description))

        user = await client_storage.request(method_name="getaccountbywallet", 
                                    wallet=owneraddr)
        if "error" in user.keys():
            return user

        balance = await client_balance.request(method_name="getbalance", uid=user["id"])

        if "error" in balance.keys():
            return balance

        common_price = int(content_fee) + int(descr_fee)

        diff = int(list(balance.values())[0]) - common_price

        if diff < 0:
            return {"error":403, "reason": "Balance is not enough."}

        decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                                amount=common_price)

        if "error" in decbalance.keys():
            return decbalance
        
        addr = contract_owner
        # blockid = await lastblockid()
        # if not verify_secret(api_pass, blockid, addr, owneraddr, cus, secret=secret):
        #     return {'error': 'Bad secret'}
        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': addr})
        qtum = init_qtum()
        r8_ipfs = R8_IPFS()

        ipfs_hash = r8_ipfs.upload_to_ipfs(cus)
        descr_hash = r8_ipfs.upload_to_ipfs(description)

        cid = r8_sc.getCID(ipfs_hash)[0]
        if cid != 0:
            return {'error': 'file was uploaded'}
        logging.debug("Before result")
        result = r8_sc.makeCID(ipfs_hash, owneraddr, descr_hash, price)

        return {'result': result, 'hash': ipfs_hash, 'cus': cus, 'addr': addr, 'owner_hex_addr': owneraddr}#, 'blockid': blockid, 'secret': secret}


    #@verify
    async def setdescrforcid(*args, **kwargs):#, addr, blockid, secret):
        message = json.loads(kwargs["message"])
        
        cid = int(message.get("cid", 0))
        descr = message.get("descr")
        owneraddr = message.get("owneraddr")

        user = await client_storage.request(method_name="getaccountbywallet", 
                                    wallet=owneraddr)
        if "error" in user.keys():
            return user

        balance = await client_balance.request(method_name="getbalance", uid=user["id"])

        if "error" in balance.keys():
            return balance

        if balance[str(user["id"])] == "Not found":
            return {"error":404, "reason":"User not found in balance"}

        fee = billing.estimate_set_descr_fee(len(descr))
        

        if int(balance[str(user["id"])]) - int(fee) < 0:
            return {"error":403, "reason":"Owner does not have enough balance."}

        decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                    amount=fee)

        if "error" in decbalance.keys():
            return decbalance

        addr = contract_owner
        # blockid = await lastblockid()
        # if not verify_secret(api_pass, blockid, addr, cid, descr, secret=secret):
        #     return {'error': 'Bad secret'}
        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': addr})
        ipfs = R8_IPFS()

        ipfs_hash = ipfs.upload_to_ipfs(descr)

        result = r8_sc.setCIDdescription(cid, ipfs_hash)

        return {'result': result, 'cid': str(cid), 'descr': descr, 'addr': addr}  # 'secret': secret, 'blockid': blockid}


    #@verify
    async def last_access_string(*args, **kwargs):
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.lastAccessString(cid)[0].decode()
        print(result)

        return result


    #@verify
    async def changeowner(*args, **kwargs):
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))
        new_owner = message.get("new_owner")
        access_string = message.get("access_string")

        user = await client_storage.request(method_name="getaccountbywallet", 
                                                wallet=new_owner)
        if "error" in user.keys():
            return user

        balance = await client_balance.request(method_name="getbalance", 
                                                uid=user["id"])

        if "error" in balance.keys():
            return balance

        fee = billing.estimate_change_owner_fee()
        
        if int(list(balance.values())[0]) - int(fee) < 0:
            return {"error":403, "reason":"New owner does not have enough balance."}

        decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                    amount=fee)

        if "error" in decbalance.keys():
            return decbalance

        addr = contract_owner_hex
        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        qtum = init_qtum()

        result = r8_sc.changeOwner(cid, new_owner, access_string)
        prev_owner_hex = r8_sc.getOwner(cid)[0][2:]
        prev_owner = qtum.fromhexaddress(prev_owner_hex)

        

        return {'result': result, 'cid': str(cid), 'new_owner': new_owner, 'access_string': access_string, 'prev_owner': prev_owner, 'contract_owner_hex': addr}


    #@verify
    async def sellcontent(*args, **kwargs):
        logging.debug("[+] -- Sell content")
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))
        buyer_address = message.get("buyer_address")
        access_string = message.get("access_string")

        user = await client_storage.request(method_name="getaccountbywallet", 
                                    wallet=buyer_address)
        if "error" in user.keys():
            return user

        balance = await client_balance.request(method_name="getbalance", uid=user["id"])

        if "error" in balance.keys():
            return balance

        fee = billing.estimate_sale_fee()
        
        if int(list(balance.values())[0]) - int(fee) < 0:
            return {"error":403, "reason": "Balance is not enough."}

        decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                    amount=fee)

        if "error" in decbalance.keys():
            return decbalance

        addr = contract_owner
        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        qtum = init_qtum()
        content_owner_hex = r8_sc.getOwner(cid)[0][2:]
        content_owner_addr = qtum.fromhexaddress(content_owner_hex)
        logging.debug(cid)
        logging.debug(buyer_address)
        logging.debug(access_string)
        try:
            result = r8_sc.sellContent(cid, buyer_address, access_string)
        except Exception as e:
            return {"error":500, "reason":str(e)}
       
        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address, 'access_string': access_string, 'content_owner': content_owner_addr, 'contract_owner_hex': addr}


    #@verify
    async def setprice(*args, **kwargs):
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))
        price = int(message.get("price", 0))
        owneraddr = message.get("owneraddr")

        fee = billing.estimate_set_price_fee()

        user = await client_storage.request(method_name="getaccountbywallet", 
                                    wallet=owneraddr)
        if "error" in user.keys():
            return user

        balance = await client_balance.request(method_name="getbalance", uid=user["id"])

        if "error" in balance.keys():
            return balance

        if balance[str(user["id"])] == "Not found":
            return {"error":404, "reason":"User not found in balance"}

        decbalance = await client_balance.request(method_name="decbalance", uid=user["id"], 
                                    amount=fee)

        if "error" in decbalance.keys():
            return decbalance

        if int(balance[str(user["id"])]) - int(fee) < 0:
            return {"error":403, "reason": "Balance is not enough."}

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})



        result = r8_sc.setPrice(cid, price)

        return {'result': result, 'cid': str(cid), 'price': price}


    #@verify
    async def getprice(*args, **kwargs):
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))

        r8_sc = Robin8_SC(contract_address)

        return r8_sc.getPrice(cid)[0]


    #@verify
    async def make_offer(*args, **kwargs):
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))
        buyer_address = message.get("buyer_address")
        price = int(message.get("price", 0))
        buyer_access_string = message.get("buyer_access_string")

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})
        logging.debug("Start result")
        result = r8_sc.makeOffer(cid, buyer_address, price, buyer_access_string)

        return {'result': result, 'cid': str(cid), 'offer_price': price,
                'buyer_address': buyer_address, 'buyer_access_string': buyer_access_string}


    #@verify
    async def reject_offer(*args, **kwargs):
        message = json.loads(kwargs["message"])

        cid = int(message.get("cid", 0))
        buyer_address = message.get("buyer_address")

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.rejectOffer(cid, buyer_address)

        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address}



bridge = Bridge()

@methods.add
async def lastblockcid(*args, **kwargs):
    result = await bridge.lastblockid(*args, **kwargs)
    return result

@methods.add
async def balance(*args, **kwargs):
    result = await bridge.balance(*args, **kwargs)
    return result

@methods.add
async def ipfscat(*args, **kwargs):
    result = await bridge.ipfscat(*args, **kwargs)
    return result

@methods.add
async def getcid(*args, **kwargs):
    result = await bridge.getcid(*args, **kwargs)
    return result

@methods.add
async def readbycid(*args, **kwargs):
    result = await bridge.readbycid(*args, **kwargs)
    return result

@methods.add
async def ownerbycid(*args, **kwargs):
    result = await bridge.ownerbycid(*args, **kwargs)
    return result

@methods.add
async def descrbycid(*args, **kwargs):
    result = await bridge.descrbycid(*args, **kwargs)
    return result

@methods.add
async def makecid(*args, **kwargs):
    result = await bridge.makecid(*args, **kwargs)
    return result

@methods.add
async def setdescrforcid(*args, **kwargs):
    result = await bridge.setdescrforcid(*args, **kwargs)
    return result

@methods.add
async def last_access_string(*args, **kwargs):
    result = await bridge.lastaccessstring(*args, **kwargs)
    return result

@methods.add
async def changeowner(*args, **kwargs):
    result = await bridge.changeowner(*args, **kwargs)
    return result

@methods.add
async def sellcontent(*args, **kwargs):
    result = await bridge.sellcontent(*args, **kwargs)
    return result

@methods.add
async def setprice(*args, **kwargs):
    result = await bridge.setprice(*args, **kwargs)
    return result

@methods.add
async def getprice(*args, **kwargs):
    result = await bridge.getprice(*args, **kwargs)
    return result

@methods.add
async def make_offer(*args, **kwargs):
    result = await bridge.make_offer(*args, **kwargs)
    return result

@methods.add
async def reject_offer(*args, **kwargs):
    result = await bridge.reject_offer(*args, **kwargs)
    return result
"""
