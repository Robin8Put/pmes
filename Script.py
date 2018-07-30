from pymongo import MongoClient
from hd_wallet import *
import settings

current_depth = 1
depth = 100
host_db = "localhost"
db_name = settings.BALANCE
coinid = "coinid"

Information_code = {
    0: "Success",
    1: "Error"
}

balance_add = {
    'amount_active': 0,
    'amount_frozen': 0
}


class AddNewUid():
    def __init__(self):
        self.client = MongoClient()
        self.database = self.client[db_name]
        self.current_depth = current_depth
        self.depth = depth

    def main(self, current_depth, depth=None):
        if current_depth and depth:
            self.extend_tree(current_depth, depth)
            result = Information_code[0]
            return result
        else:
            result = Information_code[1]
            return result

    def extend_tree(self, current_depth=None, depth=None):
        for depth_i in range(current_depth, depth):
            for type in available_coins:
                entry = create_address(type, exchange_xpublic_key, depth_i)
                collection = entry[coinid]
                db = self.database[collection]
                if not db.find_one(entry):
                    entry.update(balance_add)
                    db.insert_one(entry)


if __name__ == '__main__':
    tree_building = AddNewUid()
    result = tree_building.main(current_depth, depth)
    print(result)
