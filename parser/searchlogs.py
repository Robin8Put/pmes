from Qtum_SC import Qtum_SC
from bitcoinrpc.authproxy import AuthServiceProxy
from time import sleep


class SearchLogs():
    def __init__(self):
        types = {'''
                 "dad47273abc0ffd77faf355c6cbadd399be6d71cea08debec1bc8a6ad25cbb7f":
                     ["newCID({0[0]})", ["uint32"]],
                 "3b091bceb2d651718daea90d6dae6649eba0e737349b058a29fa3547cc8ab257":
                     ["newOffer({0[0]}, {0[1]}, {0[2]})", ["address", "uint32", "string"]],
                 "9170c205402f594bf92e77397182d7d82ef0df80da3629a76e4f0b56852644b7":
                     ["newCID({0[0]}, {0[1]}, {0[2]}, {0[3]})", ["uint32", "string", "string", "uint"]],
                 "38a9262fedac02428e492594acec49680f630e226196536d6996dafd344db1ea":
                     ["newOffer({0[0]}, {0[1]}, {0[2]}, {0[3]})", ["address", "uint32", "uint", "string"]],
                 '''
                 "fac32c520b886895c8954261adf342ba9116b9745a9f95fca8d4562dcc35b246":
                     ["newAccessLevel({0[0]}, {0[1]})", ["address", "uint8"]],
                 "fe9eb9cd9b5753fcdcf3067265314dc0f583418b7cd1dd02715cb67fb8f345da":
                     ["newCIDdescription({0[0]}, {0[1]}, {0[2]})", ["address", "uint32", "string"]],
                 "7c3c8342fbfa93f2e1121dbab5ad86d2fec259ac823365e137231b7d6c9022fd":
                     ["newOwnerForCID({0[0]}, {0[1]}, {0[2]})", ["address", "uint32", "string"]],
                 "245a245fd2fe522e76369a2473f09e2b8be60acdfdff492a8fab1b26fea77a41":
                     ["saleAccessForCID({0[0]}, {0[1]}, {0[2]})", ["address", "uint32", "string"]],
                 "a6bcc86b06e2d04b4b022e26c5ce3dd12e2aaa3e57835a3a5ab6afc2891a9928":
                     ["offerRejected({0[0]}, {0[1]})", ["address", "uint32"]],
                 "d2fb49496cad2d1e30798f48842e124dad6f0c61cc6fb67c18fde37c3ce74dd4":
                     ["newOffer({0[0]}, {0[1]}, {0[2]}, {0[3]}, {0[4]})", ["address", "uint32", "uint", "uint", "string"]],
                 "14fdb107141cf4fd210e2acfcc2b43094b54d909b94e77b131540b93d42937ce":
                     ["newCID({0[0]}, {0[1]}, {0[2]}, {0[3]}, {0[4]})", ["uint32", "string", "string", "uint", "uint"]],
                 "ad88468b4fbb35e2dc97c703f980614af53cc5ee52aa3c8b39d60a685c708241":
                     ["newReview({0[0]}, {0[1]}, {0[2]}, {0[3]})", ["address", "address", "uint32", "string"]]

                 }
        self.qtum = AuthServiceProxy("http://%s:%s@127.0.0.1:8333" % ("qtumuser", "qtum2018"))
        self.types = types

    def searchlogs(self, fromBlock, toBlock, address=None, topic=None):
        list_data = []
        c = 0
        for address_block in self.qtum.searchlogs(fromBlock, toBlock, address):
            log_block = address_block["log"]
            for iter_log in log_block:
                topics_log = iter_log["topics"]
                topics_log_first = topics_log[0]
                newOffer_hex = "9170c205402f594bf92e77397182d7d82ef0df80da3629a76e4f0b56852644b7"
                if topics_log_first in self.types.keys():
                    # if topics_log_first == newOffer_hex:
                    topics_data = iter_log["data"]
                    types_value = self.types[topics_log_first]
                    types_value_data = types_value[1]
                    types_value_string = types_value[0]
                    decoded = Qtum_SC.abi_to_params(topics_data, types_value_data)
                    '''
                    if len(decoded) == 3:
                        decoded = self.redact_len3(decoded)
                    if len(decoded) == 2:
                        decoded = self.redact_len2(decoded)
                    decoded_string = types_value_string.format(decoded)
                    '''
                    new_decode = self.change_decode(types_value_data, decoded)
                    #print(new_decode)
                    decoded_string = types_value_string.format(new_decode)
                    list_data += [decoded_string]
                else:
                    print(iter_log)
        #print(c)
        return list_data

    def storge(self, fromBlock, toBlock, address=None, topic=None):
        list_data = []
        for address_block in self.qtum.searchlogs(fromBlock, toBlock, address, topic):
            block_number = address_block["blockNumber"]
            tranasction_hash = address_block["transactionHash"]
            log_block = address_block["log"]
            for iter_log in log_block:
                topics_log = iter_log["topics"]
                topics_log_first = topics_log[0]
                #newOffer_hex = "dfcf2c9f1e0110c7afd2d0402d076c5ed57b29fa0450897162f7aca014bda34c"
                if topics_log_first in self.types.keys():
                    # if topics_log_first == newOffer_hex:
                    topics_data = iter_log["data"]
                    types_value = self.types[topics_log_first]
                    types_value_data = types_value[1]
                    types_value_string = types_value[0]
                    decoded = Qtum_SC.abi_to_params(topics_data, types_value_data)
                    new_decode = self.change_decode(types_value_data, decoded)
                    data_new = [tranasction_hash] + new_decode
                    list_data += [data_new]
                    # decoded_string = types_value_string.format(new_decode)
                    # print(decoded_string)
                else:
                    print(topics_log_first)
        return list_data

    def redact_len3(self, data):
        addresses_type = data[0]
        address_type = addresses_type[2:]
        int_type = data[1]
        bstring_type = data[2]
        string_type = bstring_type.decode()
        return [address_type] + [int_type] + [string_type]

    def redact_len2(self, data):
        addresses_type = data[0]
        address_type = addresses_type[2:]
        int_type = data[1]
        return [address_type] + [int_type]

    def str_new(self):
        for i in self.searchlogs(0, -1, {"addresses": ["f63a5d2564a4b291078115f055eda46978cd61fb"]}):
            print(i)

    def change_decode(self, signatures_list_type, decode):
        decode = list(decode)
        if "address" in signatures_list_type:
            index_adr = signatures_list_type.index("address")
            decode_index_adr = decode[index_adr]
            new_adr = decode_index_adr[2:]
            decode[index_adr] = new_adr
        if "string" in signatures_list_type:
            index_str = signatures_list_type.index("string")
            decode_index_str = decode[index_str]
            new_str = decode_index_str.decode()
            decode[index_str] = new_str
        return decode

    def getblockcount(self):
        return self.qtum.getblockcount()


if __name__ == '__main__':
    obj_searchlogs = SearchLogs()
    # searchlog = obj_searchlogs.searchlogs(0, -1, {"addresses": ["363d33ed942bd543b073101fa6e5ee00aa67cbad"]})
    obj_searchlogs.str_new()
