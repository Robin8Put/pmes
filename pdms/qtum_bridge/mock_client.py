from jsonrpcclient.http_client import HTTPClient
import codecs


def upload_image():
    decode_hex = codecs.getdecoder("hex_codec")
    encode_hex = codecs.getencoder("hex_codec")
    with open('comando.jpg', 'rb') as file:
        data = file.read()
    data = encode_hex(data)[0].decode()
    print(data)
    client = HTTPClient('http://localhost:8888')
    client.send('{"jsonrpc": "2.0", "method": "makecid", "params": {"cus": "%s", "owneraddr": "%s"}, "id": 1}' % (data, 'qgh88fssi4JrkH8LLvkqvC7SzGxvyApYis'))


def download_image(cid):
    decode_hex = codecs.getdecoder("hex_codec")
    encode_hex = codecs.getencoder("hex_codec")
    client = HTTPClient('http://localhost:8888')
    data = client.request(method_name='readbycid', cid=str(cid))
    print(data)

    with open('comando_downloaded.jpg', 'wb') as file:
        file.write(decode_hex(data.encode())[0])

if __name__=='__main__':
    #upload_image()
    download_image(11)