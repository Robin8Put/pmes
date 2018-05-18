from hashlib import sha256


def test():
    str = 'hello'.encode()
    print(sha256(sha256(str).hexdigest().encode()).hexdigest())

def double_sha256(str):
    return sha256(sha256(str).hexdigest().encode()).hexdigest()

def verify_secret(*params, secret):
    str = ''
    for p in params:
        str += p
    str = str.encode()
    print(str)
    return double_sha256(str) == secret


if __name__=='__main__':
    print(verify_secret('he', 'llo', secret='d7914fe546b684688bb95f4f888a92dfc680603a75f23eb823658031fff766d9'))