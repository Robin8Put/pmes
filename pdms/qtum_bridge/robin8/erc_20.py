from robin8 import qtum_sc


class Erc20(qtum_sc):

    def __init__(self, contract_address, qtum_rpc=None):
        func_hashes = {
            'totalSupply': '18160ddd',  # totalSupply()
            'balanceOf': '70a08231',    # balanceOf(address)
            'allowance': 'dd62ed3e',    # allowance(address,address)
            'transfer':  'a9059cbb',    # transfer(address,uint256)
            'approve':   '095ea7b3',    # approve(address,uint256)
            'transferFrom': '23b872dd',  # transferFrom(address,address,uint256)
        }

        self.topics = {
            'ddf252ad': 'Transfer',  # Transfer(address,address,uint256)
            '8c5be1e5': 'Approval'   # Approval(address,address,uint256)
        }

        super().__init__(contract_address, func_hashes, qtum_rpc)

    def totalSupply(self,):
        return self.callcontract(func_name='totalSupply', input_types=None, input_values=None,
                                 output_types=['uin256'])

    def balanceOf(self, address):
        return self.callcontract(func_name='balanceOf', input_types=['address'], input_values=[address],
                                 output_types=['uint256'])

    def allowance(self, from_addr, to_addr):
        return self.callcontract(func_name='allowance', input_types=['address', 'address'], input_values=[from_addr, to_addr],
                                 output_types=['uint256'])

    def transfer(self, to_addr, amount):
        return self.sendtocontract(func_name='transfer', input_types=['address', 'uint256'], input_values=[to_addr, amount],
                                 output_types=['bool'])

    def approve(self, addr, amount):
        return self.sendtocontract(func_name='approve', input_types=['address', 'uint256'], input_values=[addr, amount],
                                 output_types=['bool'])

    def transferFrom(self, from_addr, to_addr, amount):
        return self.sendtocontract(func_name='transferFrom', input_types=['address', 'address', 'uint256'], input_values=[from_addr, to_addr, amount],
                                 output_types=['bool'])

    def get_topic(self, topic_hash):
        return self.topics[topic_hash[:8]]
