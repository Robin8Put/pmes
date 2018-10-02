# todo: handle invalid params

from jsonrpcserver.aio import methods
from R8Blockchain.blockchain import R8Blockchain
from R8Storage.storage import R8Storage
from r8balance import R8Balance
from hashlib import sha256
from robin8_billing import robin8_billing
import logging
import json
import os
import settings
from jsonrpcclient.tornado_client import TornadoClient
from tornado_components.web import RobustTornadoClient, SignedTornadoClient
from config import storage_type, storage_host, storage_port, storage_download_time_limit, \
                    contract_owner, contract_owner_hex, contract_address, blockchain_type, \
                    decimals, ipc_path, http_provider, pmes_abi, private_key, \
                    gas_limit, gas_price
from robin8.pmes_eth_contract_handler import PmesEthContractHandler
from robin8.pmes_qtum_contract_handler import PmesQtumContractHandler
from qtum_utils.qtum import Qtum


client_storage = TornadoClient(settings.storageurl)
client_balance = TornadoClient(settings.balanceurl)

coinid = "QTUM"

def get_storage_handler():
    if storage_type == 'ipfs':
        return R8Storage.init_ipfs(host=storage_host, port=storage_port,
                                   time_limit=storage_download_time_limit)
    else:
        return R8Storage.init_no_storage()
        

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



if storage_type == 'ipfs':
    storage_handler = R8Storage.init_ipfs(host=storage_host, port=storage_port,
                               time_limit=storage_download_time_limit)
else:
    storage_handler = R8Storage.init_no_storage()

def get_storage_handler():
    storage_handler.reload_http_provider(storage_host, storage_port)
    return storage_handler


if blockchain_type == 'qtum':
    blockchain_handler = R8Blockchain.init_qtum_http(http_provider)
elif blockchain_type == 'eth':
    if ipc_path:
        blockchain_handler = R8Blockchain.init_ethereum_ipc(ipc_path)
    else:
        blockchain_handler = R8Blockchain.init_ethereum_http(http_provider)

def get_blockchain_handler():
    if ipc_path:
        blockchain_handler.reload_ipc_path(ipc_path)
    else:
        blockchain_handler.reload_http_provider(http_provider)
    return blockchain_handler


def get_eth_contract_handler():
    if ipc_path:
        return PmesEthContractHandler.from_ipc_path(ipc_path, contract_address, pmes_abi)
    else:
        return PmesEthContractHandler.from_http_provider(http_provider, contract_address, pmes_abi)

def get_qtum_contract_handler():
    return PmesQtumContractHandler.from_http_provider(http_provider, contract_address, pmes_abi)

if blockchain_type == 'qtum':
    contract_handler = get_qtum_contract_handler()
    contract_handler.set_send_params({'gasLimit': gas_limit, 'gasPrice': gas_price, 'sender': contract_owner})
elif blockchain_type == 'eth':
    contract_handler = get_eth_contract_handler()
    contract_handler.set_send_params({'gasLimit': gas_limit, 'gasPrice': gas_price, 'private_key': private_key})
else:
    raise Exception('Unknown blockchain id')

def get_contract_handler():
    if ipc_path:
        contract_handler.reload_ipc_path(ipc_path)
    else:
        contract_handler.reload_http_provider(http_provider)
    return contract_handler


def double_sha256(str):
    return sha256(sha256(str).digest()).hexdigest()


def verify_secret(*params, secret):
    return double_sha256(''.join(params)) == secret


class Bridge(object):


    #@verify
    async def test(*args, **kwargs):
        return 'It works'

    #@verify
    async def post_test(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        return 'test_param is %s' % kwargs["test"]


    #@verify
    async def lastblockid(*args, **kwarg):
        kwargs = json.loads(kwargs.get("message"))

        res = get_blockchain_handler().get_last_block_id()
        return res


    #@verify
    async def balance(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

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


    #@verify
    async def storagecat(*args, **kwargs):
        #kwargs = json.loads(kwargs.get("message"))
        hash = args[1]

        storage_handler = get_storage_handler()
        try:
            data = storage_handler.download_content(hash).decode()
        except:
            return {"error": "storage download time out"}

        if not data:
            return {"error": "storage hash not found", "code": 404}

        return data


    #@verify
    async def getcid(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        hash = kwargs.get("hash")
        r8_sc = get_contract_handler()
        cid = r8_sc.getCid(hash)
        if cid == 0:
            return {'error': 'Hash not found'}

        return str(cid)

    #@verify
    async def getcus(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        robin8 = get_contract_handler()
        cus = robin8.getCus(cid)

        if not cus:
            return {'error': 'Not found', 'code': 404}
        if cus[0:2] == 'Qm' and len(cus) > 30:
            return await storagecat(cus)
        return cus

    #@verify
    async def readbycid(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        robin8 = get_contract_handler()
        res = robin8.contents(cid)

        if res['cus'][0:2] == 'Qm' and len(res['cus']) > 30:
            res['cus'] = await storagecat(res['cus'])
        if res['description'][0:2] == 'Qm' and len(res['description']) > 30:
            res['description'] = await storagecat(res['description'])

        return res

    #@verify
    async def ownerbycid(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid", 0))
        r8_sc = get_contract_handler()

        owner_hex_addr = r8_sc.getOwner(cid)
        if not owner_hex_addr:
            return {'error': 'Not found', 'code': 404}
        if owner_hex_addr.replace('0', '') == '':
            return {'error': 'Not found', 'code': 404}

        blockchain_handler = get_blockchain_handler()

        #owneraddr = blockchain_handler.from_hex_address(owner_hex_addr)

        return owner_hex_addr

    #@verify
    async def descrbycid(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        r8_sc = get_contract_handler()

        descr = r8_sc.getDescription(cid)
        if not descr:
            return {'error': 'Not found', 'code': 404}

        if descr[0:2] == 'Qm' and len(descr) > 30:
            return await storagecat(descr)

        return descr

    #@verify
    async def makecid(*args, **kwargs):
        logging.debug("\n\n Make cid debugging. ")
        kwargs = json.loads(kwargs.get("message"))
        cus = kwargs.get("cus")
        owneraddr = "0x" + kwargs.get("owneraddr")
        description = kwargs.get("description")
        read_price = int(kwargs.get("read_price", 0))
        write_price = int(kwargs.get("write_price", 0))

        logging.debug(kwargs)
        addr = contract_owner

        r8_sc = get_contract_handler()

        storage_handler = get_storage_handler()

        logging.debug("\n   *    Storage handler. ")
        logging.debug(storage_handler)

        logging.debug("\n\n   *    Cus hash and descr_hash.")
        cus_hash = storage_handler.upload_content(cus)
        logging.debug(cus_hash)
        descr_hash = storage_handler.upload_content(description)
        logging.debug(descr_hash)

        logging.debug("\n  *   Cid")
        cid = r8_sc.getCid(cus_hash)
        logging.debug(cid)
        if cid != 0:
            return {'error': 'file was uploaded'}

        result = r8_sc.makeCid(cus_hash, owneraddr, descr_hash, read_price, write_price)

        return {'result': result, 'cus_hash': cus_hash, 'cus': cus, 'addr': addr, 'owner_hex_addr': owneraddr,
                'descr_hash': descr_hash}

    #@verify
    async def setdescrforcid(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        descr = kwargs.get("descr")

        addr = contract_owner

        r8_sc = get_contract_handler()
        storage_handler = get_storage_handler()

        descr_hash = storage_handler.upload_content(descr)

        result = r8_sc.setDescription(cid, descr_hash)

        return {'result': result, 'cid': str(cid), 'descr': descr, 'addr': addr, 'descr_hash': descr_hash}

    #@verify
    async def changeowner(*args, **kwargs):
        logging.debug("[+] -- Change owner")
        kwargs = json.loads(kwargs.get("message"))
        cid = int(kwargs.get("cid"))
        new_owner = kwargs.get("new_owner")
        access_string = kwargs.get("access_string")
        logging.debug("\n\n")
        logging.debug(access_string)
        logging.debug(type(access_string))
        logging.debug("\n\n")
        seller_public_key = kwargs.get("seller_public_key")

        addr = contract_owner_hex
        r8_sc = get_contract_handler()

        blockchain_handler = get_blockchain_handler()

        result = r8_sc.changeOwner(cid, new_owner, seller_public_key, access_string)
        
        prev_owner_hex = r8_sc.getOwner(cid)
        
        prev_owner = blockchain_handler.from_hex_address(prev_owner_hex)

        return {'result': result, 'cid': str(cid), 'new_owner': new_owner,
                'access_string': access_string, 'prev_owner': prev_owner, 'contract_owner_hex': addr}

    #@verify
    async def sellcontent(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        buyer_address = kwargs.get("buyer_address")
        access_string = kwargs.get("access_string")
        seller_public_key = kwargs.get("seller_public_key")

        addr = contract_owner
        r8_sc = get_contract_handler()

        blockchain_handler = get_blockchain_handler()
        content_owner_hex = r8_sc.getOwner(cid)
        content_owner_addr = blockchain_handler.from_hex_address(content_owner_hex)

        result = r8_sc.sellContent(cid, buyer_address, seller_public_key, access_string)

        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address,
                'access_string': access_string, 'content_owner': content_owner_addr, 'contract_owner_hex': addr}

    #@verify
    async def set_read_price(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        price = kwargs.get("read_price")

        r8_sc = get_contract_handler()

        result = r8_sc.setReadPrice(cid, price)

        return {'result': result, 'cid': str(cid), 'price': price}

    #@verify
    async def set_write_price(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        price = kwargs.get("write_price")

        r8_sc = get_contract_handler()

        result = r8_sc.setWritePrice(cid, price)

        return {'result': result, 'cid': str(cid), 'price': price}

    #@verify
    async def get_read_price(*args, **kwargs):

        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))

        r8_sc = get_contract_handler()

        return r8_sc.getReadPrice(cid)

    #@verify
    async def get_write_price(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))
        cid = int(kwargs.get("cid"))
        r8_sc = get_contract_handler()

        return r8_sc.getWritePrice(cid)

    #@verify
    async def make_offer(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))

        cid = int(kwargs.get("cid"))
        buyer_address = kwargs.get("buyer_address")
        offer_type = int(kwargs.get("offer_type"))
        price = kwargs.get("read_price") or kwargs.get("write_price")
        buyer_access_string = kwargs.get("buyer_access_string")
        price = int(price)

        r8_sc = get_contract_handler()

        result = r8_sc.makeOffer(cid, "0x" + buyer_address, offer_type, price, buyer_access_string)
        return {'result': result, 'cid': str(cid), 'offer_price': price,
                'buyer_address': buyer_address, 'buyer_access_string': buyer_access_string, 'offer_type': offer_type}

    #@verify
    async def reject_offer(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))


        cid = int(kwargs.get("cid"))
        buyer_address = kwargs.get("buyer_address")

        r8_sc = get_contract_handler()

        result = r8_sc.rejectOffer(cid, buyer_address)

        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address}

    #@verify
    async def add_review(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))
        cid = kwargs.get("cid")
        buyer_address = kwargs.get("buyer_address")
        stars = kwargs.get("stars")
        review = kwargs.get("review")

        r8_sc = get_contract_handler()

        storage_handler = get_storage_handler()
        review_hash = storage_handler.upload_content(str(stars)+review)

        review_hash = storage_handler.upload_content(str(stars)+buyer_address+review)

        result = r8_sc.addReview(cid, "0x" + buyer_address, review_hash)

        return {'result': result, 'cid': str(cid), 'buyer_address': buyer_address}

    #@verify
    async def get_next_cid(*args, **kwargs):
        r8_sc = get_contract_handler()

        r8_sc.nextCid()        

        return {'next_cid': r8_sc.nextCid()}

    #@verify
    async def get_cid_offers(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))
        handler = get_contract_handler()
        cid = int(kwargs.get("cid"))
        offers = handler.get_cid_offers(cid)
        for offer in offers:
            offer["coinid"] = coinid
        result =  [off for off in offers if off["status"] != 2]

        logging.debug(result)
        return result

    #@verify
    async def get_buyer_offers(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))
        handler = get_contract_handler()
        res = []
        buyer_address = str(kwargs.get("buyer_address"))
        offers = handler.get_buyer_offers(buyer_address)
        for offer in offers:
            offer["coinid"] = coinid
        #result =  [off for off in offers if off["status"] != 2 and off["status"] != 1]

        return offers

    #@verify
    async def get_reviews(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))
        handler = get_contract_handler()
        storage_handler = get_storage_handler()
        res = []
        cid = int(kwargs.get("cid"))
        reviews = handler.get_reviews(cid)
        for r in reviews:
            r = storage_handler.download_content(r).decode()
            res.append({'rating': r[0], 'buyer_address': r[1:41], 
                            'review': r[41:]})

        return res

    #@verify
    async def get_all_content(*args, **kwargs):
        kwargs = json.loads(kwargs.get("message"))
        range_ = kwargs.get("range_")
        contents = []
        last_cid = await get_next_cid()
        for counter in range(*tuple(range_)):
            data = {}
            write_price = await get_write_price(message=json.dumps({"cid": counter}))
            read_price = await get_read_price(message=json.dumps({"cid": counter}))
            description = await descrbycid(message=json.dumps({"cid": counter}))

            if write_price == 0 and read_price == 0:
                break

            else:
                owneraddr = await bridge.ownerbycid(message=json.dumps({"cid":counter}))
                data["owneraddr"] = owneraddr
                data["write_price"] = write_price
                data["read_price"] = read_price
                data["description"] = description
                data["cid"] = counter
                data["coinid"] = coinid

                contents.append(data)

        return contents

    #@verify
    async def get_single_content(*args, **kwargs):
        message = json.loads(kwargs.get("message"))

        cid = message.get("cid")

        data = {}

        write_price = await get_write_price(message=json.dumps({"cid": cid}))
        read_price = await get_read_price(message=json.dumps({"cid": cid}))
        description = await descrbycid(message=json.dumps({"cid": cid}))
        owneraddr = await ownerbycid(message=json.dumps({"cid": cid}))
        cus = await getcus(message=json.dumps({"cid":cid}))


        data["owneraddr"] = owneraddr
        data["write_access"] = write_price
        data["read_access"] = read_price
        data["description"] = description
        data["cid"] = cid
        data["coinid"] = coinid
        data["content"] = cus

        return data

    #@verify
    async def get_users_content(*args, **kwargs):

        message = json.loads(kwargs.get("message"))
        cids = json.loads(message.get("cids"))
        logging.debug("\n\n")
        logging.debug("[+] -- Get users content debugging. ")
        logging.debug(cids)

        container = []

        for cid in cids:

            data = {}

            if not cid[0]:
                data["owneraddr"] = None
                data["write_access"] = None
                data["read_access"] = None
                data["description"] = None
                data["cid"] = None
                data["coinid"] = None
                data["txid"] = "https://testnet.qtum.org/tx/" + str(cid[1])
                container.append(data)
                continue

            else:

                write_price = await get_write_price(message=json.dumps({"cid": cid[0]}))
                read_price = await get_read_price(message=json.dumps({"cid": cid[0]}))
                description = await descrbycid(message=json.dumps({"cid": cid[0]}))
                owneraddr = await ownerbycid(message=json.dumps({"cid": cid[0]}))

                data["owneraddr"] = owneraddr
                data["write_access"] = write_price
                data["read_access"] = read_price
                data["description"] = description
                data["cid"] = cid[0]
                data["coinid"] = coinid
                data["txid"] = "https://testnet.qtum.org/tx/" + str(cid[1])
                container.append(data)

        return container

    #@verify
    async def get_offer(*args, **kwargs):
        logging.debug("[+] -- Get offer. ")
        kwargs = json.loads(kwargs.get("message"))
        handler = get_contract_handler()
        
        cid = int(kwargs.get("cid"))
        logging.debug(cid)
        buyer_address = kwargs.get("buyer_address")
        logging.debug(buyer_address)
        offer_id = handler.CidBuyerIdToOfferId(cid, buyer_address)
        
        return handler.offers(offer_id)


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
async def storagecat(*args, **kwargs):
    result = await bridge.storagecat(*args, **kwargs)
    return result

@methods.add
async def getcid(*args, **kwargs):
    result = await bridge.getcid(*args, **kwargs)
    return result

@methods.add
async def getcus(*args, **kwargs):
    result = await bridge.getcus(*args, **kwargs)
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

@methods.add
async def get_next_cid(*args, **kwargs):
    result = await bridge.get_next_cid(*args, **kwargs)
    return result

@methods.add
async def get_cid_offers(*args, **kwargs):
    result = await bridge.get_cid_offers(*args, **kwargs)
    return result

@methods.add
async def get_buyer_offers(*args, **kwargs):
    result = await bridge.get_buyer_offers(*args, **kwargs)
    return result

@methods.add
async def get_next_cid(*args, **kwargs):
    result = await bridge.get_next_cid(*args, **kwargs)
    return result


@methods.add
async def getallcontent(*args, **kwargs):
    result = await bridge.get_all_content(*args, **kwargs)
    return result

@methods.add 
async def getsinglecontent(*args, **kwargs):
    result = await bridge.get_single_content(*args, **kwargs)
    return result 

@methods.add 
async def getuserscontent(*args, **kwargs):
    logging.debug("[+] -- Get users content")
    result = await bridge.get_users_content(*args, **kwargs)
    return result 

@methods.add
async def get_reviews(*args, **kwargs):
    result = await bridge.get_reviews(*args, **kwargs)
    return result

@methods.add
async def get_offer(*args, **kwargs):
    result = await bridge.get_offer(*args, **kwargs)
    return result