from bitcoinrpc.authproxy import AuthServiceProxy
from hashlib import sha256
import codecs


class Qtum_Blockchain:
    def __init__(self, qtum_rpc=None):
        self.reload_rpc(qtum_rpc)

        self.decode_hex = codecs.getdecoder("hex_codec")
        self.encode_hex = codecs.getencoder("hex_codec")

    def reload_rpc(self, qtum_rpc=None):
        if qtum_rpc is None:
            self.qtum_rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018"))
        elif type(qtum_rpc) is int:
            self.qtum_rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:%d" %
                                             ("qtumuser", "qtum2018", qtum_rpc))  # port specified
        else:
            self.qtum_rpc = qtum_rpc

    def get_lastblockid(self):
        last_block_heigh = self.qtum_rpc.getblockcount()
        last_block_hash = self.qtum_rpc.getblockhash(last_block_heigh)

        l = sha256(self.decode_hex(last_block_hash)[0]).hexdigest()
        r = hex(last_block_heigh)

        res = l[0:10] + r[2:].rjust(10, '0')
        return res


if __name__=='__main__':
    q = Qtum_Blockchain()
    print(q.get_lastblockid())
