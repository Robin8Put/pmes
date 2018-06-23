# todo: handle invalid params

from jsonrpcserver.aio import methods
from R8Blockchain.blockchain import R8Blockchain
from R8Storage.storage import R8Storage
from robin8.robin8_sc import Robin8_SC
from r8balance import R8Balance
from hashlib import sha256
from qtum_utils.qtum import Qtum
from robin8_billing import robin8_billing
import logging
import json
import os
import settings
from jsonrpcclient.http_client import HTTPClient
from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import RobustTornadoClient, SignedTornadoClient 
from config import storage_type, storage_host, storage_port, storage_download_time_limit, \
                    contract_owner, contract_owner_hex, contract_address, blockchain_type, \
                    decimals, blockchain_username, blockchain_password, \
                    blockchain_host, blockchain_port


billing = robin8_billing.Robin8_Billig("robin8_billing/billing")
#billing = robin8_billing.Robin8_Billig("pdms/qtum_bridge/robin8_billing/billing")
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
        logging.debug(signature)
        try:
            flag = Qtum.verify_message(message, signature, pubkey)
        except Exception as e:
            flag = None
        if not flag:
            result =  {"error":403, "reason":"Invalid signature"}
        else:
            result = await func(*args, **kwargs)
        return result
    return wrapper



def get_storage_handler():
    if storage_type == 'ipfs':
        return R8Storage.init_ipfs(host=storage_host, port=storage_port,
                                   time_limit=storage_download_time_limit)
    else:
        return R8Storage.init_no_storage()


def get_blockchain_handler():
    if blockchain_type == 'qtum':
        return R8Blockchain.init_qtum(blockchain_host, blockchain_port,
                                      blockchain_username, blockchain_password)

    elif blockchain_type == 'eth':
        return R8Blockchain.init_ethereum(blockchain_host, blockchain_port,
                                      blockchain_username, blockchain_password)


def double_sha256(str):
    return sha256(sha256(str).digest()).hexdigest()


def verify_secret(*params, secret):
    return double_sha256(''.join(params)) == secret



class Bridge(object):


    @verify
    async def test(*args, **kwargs):
        return 'It works'

    @verify
    async def post_test(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        return 'test_param is %s' % message["test"]


    @verify
    async def lastblockid(*args, **kwarg):
        res = get_blockchain_handler().get_last_block_id()
        return res


    @verify
    async def balance(*args, **kwargs):
        blockchain_handler = get_blockchain_handler()
        unspent = blockchain_handler.get_unspent()
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
        addr_arr['getbl'] = float(blockchain_handler.get_balance())

        encoded_arr = {k: R8Balance(v, decimals).get_balance() for k, v in addr_arr.items()}
        encoded_arr['decimals'] = decimals
        return encoded_arr


    @verify
    async def storagecat(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        hash = message.get("hash")
        storage_handler = get_storage_handler()
        try:
            data = storage_handler.download_content(hash).decode()
        except:
            return {"error": "storage download time out"}

        if not data:
            return {"error": "storage hash not found", "code": 404}

        return data


    @verify
    async def getcid(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        hash = message.get("hash")
        r8_sc = Robin8_SC(contract_address)
        cid = r8_sc.getCID(hash)[0]
        if cid == 0:
            return {'error': 'Hash not found'}

        return str(cid)


    @verify
    async def readbycid(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        robin8 = Robin8_SC(contract_address)
        cus = robin8.getCUS(cid)[0].decode()

        if not cus:
            return {'error': 'Not found', 'code': 404}
        if cus[0:2] == 'Qm' and len(cus) > 30:
            return await storagecat(cus)
        return cus


    @verify
    async def ownerbycid(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid", 0))
        r8_sc = Robin8_SC(contract_address)

        owner_hex_addr = r8_sc.getOwner(cid)[0]
        if not owner_hex_addr:
            return {'error': 'Not found', 'code': 404}
        owner_hex_addr = owner_hex_addr[2:]  # remove 0x
        if owner_hex_addr.replace('0', '') == '':
            return {'error': 'Not found', 'code': 404}
        blockchain_handler = get_blockchain_handler()

        owneraddr = blockchain_handler.from_hex_address(owner_hex_addr)

        return owner_hex_addr

    @verify
    async def descrbycid(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        r8_sc = Robin8_SC(contract_address)

        descr = r8_sc.CIDtoDescription(cid)[0].decode()
        if not descr:
            return {'error': 'Not found', 'code': 404}

        if descr[0:2] == 'Qm' and len(descr) > 30:
            return await storagecat(descr)

        return descr

    @verify
    async def makecid(*args, **kwargs):
        message = json.loads(kwargs.get("message"))
        cus = message.get("cus")
        owneraddr = message.get("owneraddr")
        description = message.get("description")
        read_price = int(message.get("read_price", 0))
        write_price = int(message.get("write_price", 0))

        addr = contract_owner

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': addr})

        storage_handler = get_storage_handler()

        cus_hash = storage_handler.upload_content(cus)
        descr_hash = storage_handler.upload_content(description)

        cid = r8_sc.getCID(cus_hash)[0]
        if cid != 0:
            return {'error': 'file was uploaded'}

        result = r8_sc.makeCID(cus_hash, owneraddr, descr_hash, read_price, write_price)

        return {'result': result, 'cus_hash': cus_hash, 'cus': cus, 'addr': addr, 'owner_hex_addr': owneraddr,
                'descr_hash': descr_hash}


    @verify
    async def setdescrforcid(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        descr = message.get("descr")

        addr = contract_owner

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': addr})
        storage_handler = get_storage_handler()

        descr_hash = storage_handler.upload_content(descr)

        result = r8_sc.setCIDdescription(cid, descr_hash)

        return {'result': result, 'cid': str(cid), 'descr': descr, 'addr': addr, 'descr_hash': descr_hash}

    @verify
    async def last_access_string(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.lastAccessString(cid)[0].decode()

        return result

    @verify
    async def changeowner(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        new_owner = message.get("new_owner")
        access_string = message.get("access_string")

        addr = contract_owner_hex
        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        blockchain_handler = get_blockchain_handler()

        result = r8_sc.changeOwner(cid, new_owner, access_string)
        prev_owner_hex = r8_sc.getOwner(cid)[0][2:]
        prev_owner = blockchain_handler.from_hex_address(prev_owner_hex)

        return {'result': result, 'cid': str(cid), 'new_owner': new_owner,
                'access_string': access_string, 'prev_owner': prev_owner, 'contract_owner_hex': addr}

    @verify
    async def sellcontent(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        buyer_address = message.get("buyer_address")
        access_string = message.get("access_string")

        addr = contract_owner
        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        blockchain_handler = get_blockchain_handler()
        content_owner_hex = r8_sc.getOwner(cid)[0][2:]
        content_owner_addr = blockchain_handler.from_hex_address(content_owner_hex)

        result = r8_sc.sellContent(cid, buyer_address, access_string)

        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address,
                'access_string': access_string, 'content_owner': content_owner_addr, 'contract_owner_hex': addr}

    @verify
    async def set_read_price(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        price = int(message.get("read_price"))

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.setReadPrice(cid, int(price))

        return {'result': result, 'cid': str(cid), 'price': price}


    @verify
    async def set_write_price(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        price = int(message.get("write_price"))

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.setWritePrice(cid, int(price))

        return {'result': result, 'cid': str(cid), 'price': price}


    @verify
    async def get_read_price(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))

        r8_sc = Robin8_SC(contract_address)

        return r8_sc.getReadPrice(cid)[0]


    @verify
    async def get_write_price(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))

        r8_sc = Robin8_SC(contract_address)

        return r8_sc.getWritePrice(cid)[0]


    @verify
    async def make_offer(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        buyer_address = message.get("buyer_address")
        offer_type = message.get("offer_type")
        price = message.get("read_price") or message.get("write_price")
        buyer_access_string = message.get("buyer_access_string")
        price = int(price)

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.makeOffer(int(cid), buyer_address, int(offer_type), int(price), buyer_access_string)

        return {'result': result, 'cid': str(cid), 'offer_price': price,
                'buyer_address': buyer_address, 'buyer_access_string': buyer_access_string, 'offer_type': offer_type}


    @verify
    async def reject_offer(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = int(message.get("cid"))
        buyer_address = message.get("buyer_address")

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.rejectOffer(cid, buyer_address)

        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address}


    @verify
    async def add_review(*args, **kwargs):
        message = json.loads(kwargs.get("message"))
        cid = int(message.get("cid"))
        buyer_address = message.get("buyer_address")
        stars = message.get("stars")
        review = message.get("review")

        r8_sc = Robin8_SC(contract_address)
        r8_sc.set_send_params({'sender': contract_owner})

        result = r8_sc.addReview(buyer_address, cid, str(stars) + review)

        return {'result': result, 'cid': str(cid), 'buyer_addr': buyer_address}





bridge = Bridge()

@methods.add
async def test(*args, **kwargs):
    return bridge.test()

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
    result = await bridge.last_access_string(*args, **kwargs)
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
async def set_read_price(*args, **kwargs):
    result = await bridge.set_read_price(*args, **kwargs)
    return result

@methods.add
async def set_write_price(*args, **kwargs):
    result = await bridge.set_write_price(*args, **kwargs)
    return result

@methods.add
async def get_read_price(*args, **kwargs):
    result = await bridge.get_read_price(*args, **kwargs)
    return result

@methods.add
async def get_write_price(*args, **kwargs):
    result = await bridge.get_write_price(*args, **kwargs)
    return result

@methods.add
async def make_offer(*args, **kwargs):
    result = await bridge.make_offer(*args, **kwargs)
    return result

@methods.add
async def reject_offer(*args, **kwargs):
    result = await bridge.reject_offer(*args, **kwargs)
    return result

@methods.add
async def add_review(*args, **kwargs):
    result = await bridge.add_review(*args, **kwargs)
    return result
