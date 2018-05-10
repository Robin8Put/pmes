import json


class Robin8_Billig():

    def __init__(self, config_filename):
        with open(config_filename) as config:
            data = config.read()
        data = json.loads(data)
        print(data)
        self.sell_content_fee = float(data['sell_content_fee'])
        self.change_owner_fee = float(data['change_owner_fee'])
        self.set_access_level_fee = float(data['set_access_level_fee'])
        self.make_cid_fee = float(data['make_cid_fee'])
        self.set_descr_fee = float(data['set_descr_fee'])
        self.gasLimit = float(data['gasLimit'])
        self.gasPrice = float(data['gasPrice'])
        self.price_per_kilobyte = float(data['price_per_kilobyte'])

    def estimate_upload_fee(self, length):
        return self.make_cid_fee + self.gasLimit*self.gasPrice + (length // 1000)*self.price_per_kilobyte

    def estimate_sale_fee(self):
        return self.sell_content_fee + self.gasLimit*self.gasPrice

    def estimate_change_owner_fee(self):
        return self.change_owner_fee + self.gasLimit*self.gasPrice

    def estimate_set_access_level_fee(self):
        return self.set_access_level_fee + self.gasLimit*self.gasPrice

    def estimate_set_descr_fee(self, length):
        return self.set_descr_fee + self.gasLimit*self.gasPrice + (length // 1000)*self.price_per_kilobyte


if __name__ == '__main__':
    print(Robin8_Billig('billing').estimate_upload_fee(5000))
    print(Robin8_Billig('billing').estimate_sale_fee())
    print(Robin8_Billig('billing').estimate_change_owner_fee())
    print(Robin8_Billig('billing').estimate_set_access_level_fee())
    print(Robin8_Billig('billing').estimate_set_descr_fee(5000))
