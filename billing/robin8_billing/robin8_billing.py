import json


class Robin8_Billig():

    def __init__(self, config_filename):
        with open(config_filename) as config:
            data = config.read()
        data = json.loads(data)
        print(data)
        self.robin8_fee = float(data['robin8_fee'])
        self.gasLimit = float(data['gasLimit'])
        self.gasPrice = float(data['gasPrice'])
        self.price_per_kilobyte = float(data['price_per_kilobyte'])

    def estimate_upload_fee(self, length):
        return self.robin8_fee + self.gasLimit*self.gasPrice + (length // 1000)*self.price_per_kilobyte

    def estimate_sale_fee(self):
        return self.robin8_fee + self.gasLimit*self.gasPrice


if __name__ == '__main__':
    print(Robin8_Billig('billing').estimate_upload_fee(5000))
