import json


class Robin8_Billig():

    def __init__(self, billing):
        self.__dict__.update(billing)
        self.blockchain_fee = int((self.gasLimit*self.gasPrice/1e18)*(self.put_price))

    def estimate_upload_fee(self, length):
        return self.make_cid_fee + self.blockchain_fee

    def estimate_sale_fee(self):
        return self.sell_content_fee + self.blockchain_fee

    def estimate_change_owner_fee(self):
        return self.change_owner_fee + self.blockchain_fee

    def estimate_set_access_level_fee(self):
        return self.set_access_level_fee + self.blockchain_fee

    def estimate_set_descr_fee(self, length):
        return self.set_descr_fee + self.blockchain_fee

    def estimate_set_price_fee(self):
        return self.set_price_fee + self.blockchain_fee

    def estimate_make_offer_fee(self):
        return self.make_offer_fee + self.blockchain_fee

if __name__ == '__main__':
    with open('qtum_settings.json', 'rb') as f:
        billing = json.load(f)['billing']

    print(billing)

    billing_handler = Robin8_Billig(billing)
    print(billing_handler.estimate_upload_fee(0))
    print(billing_handler.estimate_sale_fee())
