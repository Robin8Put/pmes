# Builtins
import json
import logging

# Third-party
import pymongo
import time


class Table(object):
    """Custom driver for writing data to mongodb
    By default database name is 'profile_management_system',
            collection name is 'history'
    """

    def __init__(self, db_name=None, collection=None):
        # Set database parameters
        if not db_name:
            self.db_name = "profile_management_system"
        else:
            self.db_name = db_name
        if not collection:
            self.collection = "email"
        else:
            self.collection = collection

        self.client = pymongo.MongoClient("localhost")

        self.database = self.client[self.db_name]

        # Set collection nsme
        self.email = self.database[self.collection]

    def insert(self, id = None, **data):
        try:
            if self.email.find_one({"id": id}):
                return {2: "Denied"}
            else:
                if id:
                    data.update({"id": id})
                self.email.insert_one(data)
                return {0: "Success"}
        except:
            return {1: "Failed"}

    def find(self, data=None):
        if not data:
            return {3: "Missing data"}
        if self.email.find_one(data):
            dict_data = self.email.find_one(data)
            try:
                return dict_data["id"]
            except:
                return dict_data

    def read(self, *ids):
        if None not in ids:
            list_dict = []
            for i in ids:
                if self.email.find_one({"id": i}):
                    for j in self.email.find({"id": i}):
                        list_dict += [j]
            return list_dict
        else:
            return [{3: "Missing id"}]

    def update(self, id=None, **new_data):
        data = {"id": id}
        if not id:
            return {3: "Missing id"}
        elif self.email.find_one(data):
            self.email.update_one(data, {"$set": new_data})
            return {0: "Success"}
        else:
            return {2: "Denied"}

    def delete(self, id=None):
        if not id:
            return {3: "Missing data"}
        if self.email.find_one({"id": id}):
            self.email.delete_one({"id": id})
            return {0: "Success"}
        else:
            return {4: "Not found"}

    def pop_100el(self):
        mass = []
        for i in self.email.find({"time": {"$lt": time.time()}})[:100]:
            mass += [i]
            self.email.find_one_and_delete(i)
        return mass

    def count(self, data):
        return self.email.find(data).count()

    def show_db(self):
        #count = 0
        for i in self.email.find():
            #count += 1
            print(i)
        #print(count)


if __name__ == "__main__":
    err = {"a": "z"}
    db = Table()
    db.insert(err)
    print(db.insert({"a": "r"}, 13))
    db.show_db()
    print(db.read((13,)))
