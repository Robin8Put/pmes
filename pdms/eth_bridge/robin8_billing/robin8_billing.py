import json


class Robin8_Billig():

    def __init__(self, config_filename):
        with open(config_filename) as config:
            data = config.read()
        data = json.loads(data)
        print(data)
        self.sell_content_fee = int(data['sell_content_fee'])
        self.change_owner_fee = int(data['change_owner_fee'])
        self.set_access_level_fee = int(data['set_access_level_fee'])
        self.set_price_fee = int(data['set_price_fee'])
        self.make_offer_fee = int(data['make_offer_fee'])
        self.make_cid_fee = int(data['make_cid_fee'])
        self.set_descr_fee = int(data['set_descr_fee'])
        self.gasLimit = int(data['gasLimit'])
        self.gasPrice = float(data['gasPrice'])
        self.price_per_kilobyte = int(data['price_per_kilobyte'])
        self.decimals = pow(10,int(data["decimals"]))

    def estimate_upload_fee(self, length):
        return self.make_cid_fee + int((self.gasLimit*self.gasPrice)*self.decimals) + (length // 1000)*self.price_per_kilobyte

    def estimate_sale_fee(self):
        return self.sell_content_fee + (self.gasLimit*self.gasPrice)*self.decimals

    def estimate_change_owner_fee(self):
        return self.change_owner_fee + (self.gasLimit*self.gasPrice)*self.decimals

    def estimate_set_access_level_fee(self):
        return self.set_access_level_fee + (self.gasLimit*self.gasPrice)*self.decimals

    def estimate_set_descr_fee(self, length):
        return self.set_descr_fee + (self.gasLimit*self.gasPrice)*self.decimals + (length // 1000)*self.price_per_kilobyte

    def estimate_set_price_fee(self):
        return self.set_price_fee + (self.gasLimit*self.gasPrice)*self.decimals

    def estimate_make_offer_fee(self):
        return self.make_offer_fee + (self.gasLimit*self.gasPrice)*self.decimals


