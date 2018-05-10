# todo: handle invalid params

from jsonrpcserver.aio import methods
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from R8_IPFS import R8_IPFS
from robin8.Robin8_SC import Qtum_SC, Robin8_SC
from R8_Balance import R8_Balance
from hashlib import sha256
from qtum_blockchain.qtum_blockchain import Qtum_Blockchain


contract_owner = 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'
contract_owner_hex = 'fdc1ae05c161833cdf135863e332126e15d7568c'
contract_address = 'c77bb015ea904be419c9214f13daf0e071e7df1f'
decimals = 8


api_pass = 'AP'


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
            return {"error": "ipfs not read"}
        else:
            return {"error": "ipfs hash not found", "code": 404}

    return ipfs_data


@methods.add
async def getcid(hash):

    r8_sc = Robin8_SC(contract_address)
    cid = r8_sc.getCID(hash)[0]
    if cid == 0:
        return {'error': 'Hash not found'}

    return str(cid)



@methods.add
async def readbycid(cid):
    robin8 = Robin8_SC(contract_address)
    cus = robin8.getCUS(cid)[0].decode()

    if not cus:
        return {'error': 'Not found', 'code': 404}
    if cus[0:2] == 'Qm' and len(cus) > 30:
        return await ipfscat(cus)
    return cus


@methods.add
async def ownerbycid(cid):
    cid = int(cid)
    r8_sc = Robin8_SC(contract_address)

    owner_hex_addr = r8_sc.getOwner(cid)[0]
    if not owner_hex_addr:
        return {'error': 'Not found', 'code': 404}
    owner_hex_addr = owner_hex_addr[2:]  # remove 0x
    if owner_hex_addr.replace('0', '') == '':
        return {'error': 'Not found', 'code': 404}
    qtum = init_qtum()

    owneraddr = qtum.fromhexaddress(owner_hex_addr)

    return owner_hex_addr


@methods.add
async def descrbycid(cid):
    r8_sc = Robin8_SC(contract_address)

    descr = r8_sc.CIDtoDescription(cid)[0].decode()
    if not descr:
        return {'error': 'Not found', 'code': 404}

    if descr[0:2] == 'Qm' and len(descr) > 30:
        return await ipfscat(descr)

    return descr


@methods.add
async def makecid(cus, owneraddr): #addr, blockid, secret):
    addr = contract_owner
    # blockid = await lastblockid()
    # if not verify_secret(api_pass, blockid, addr, owneraddr, cus, secret=secret):
    #     return {'error': 'Bad secret'}
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': addr})
    qtum = init_qtum()
    r8_ipfs = R8_IPFS()

    ipfs_hash = r8_ipfs.upload_to_ipfs(cus)

    cid = r8_sc.getCID(ipfs_hash)[0]
    print(cid)
    if cid != 0:
        return {'error': 'file was uploaded'}

    result = r8_sc.makeCID(ipfs_hash, owneraddr)
    print(result)

    return {'result': result, 'hash': ipfs_hash, 'cus': cus, 'addr': addr, 'owner_hex_addr': owneraddr}#, 'blockid': blockid, 'secret': secret}


@methods.add
async def setdescrforcid(cid, descr):#, addr, blockid, secret):
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
    addr = contract_owner_hex
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})

    qtum = init_qtum()

    result = r8_sc.changeOwner(cid, new_owner, access_string)
    prev_owner_hex = r8_sc.getOwner(cid)[0][2:]
    prev_owner = qtum.fromhexaddress(prev_owner_hex)

    return {'result': result, 'cid': str(cid), 'new_owner': new_owner, 'access_string': access_string, 'prev_owner': prev_owner, 'contract_owner_hex': addr}


@methods.add
async def sellcontent(cid, buyer_addr, access_string):
    addr = contract_owner
    r8_sc = Robin8_SC(contract_address)
    r8_sc.set_send_params({'sender': contract_owner})

    qtum = init_qtum()
    content_owner_hex = r8_sc.getOwner(cid)[0][2:]
    content_owner_addr = qtum.fromhexaddress(content_owner_hex)

    result = r8_sc.sellContent(cid, buyer_addr, access_string)

    return {'result': result, 'cid': str(cid), 'buyer_addr': buyer_addr, 'access_string': access_string, 'content_owner': content_owner_addr, 'contract_owner_hex': addr}
