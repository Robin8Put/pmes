from time import time
import pymongo


class Table(object):
    """Custom driver for writing data to mongodb
    By default database name is 'pmes',
             collection name is 'email'
    Methods:
        insert - create new documents. Get id and data for update
        find - find id for input data
        read - find data for input id
        update - update documents
        delete - delete documents
    """

    def __init__(self, db_name=None, collection=None):
        # Set database parameters
        if not db_name:
            self.db_name = "pmes"
        else:
            self.db_name = db_name
        if not collection:
            self.collection = "email"
        else:
            self.collection = collection

        self.client = pymongo.MongoClient("localhost")

        self.database = self.client[self.db_name]

        # Set collection name
        self.email = self.database[self.collection]

    def insert(self, id=None, **data):
        # insert - create new documents. Get id and data for update
        try:
            if id:
                data.update({"id": id})
                if self.email.find_one({"id": id}):
                    return "Denied"
            insertedId = self.email.insert_one(data).inserted_id
            return "Success"
        except:
            return "Failed"

    def find(self, data=None):
        # find - find id for input data
        if not data:
            return "Missing data"
        if self.email.find_one(data):
            dict_data = self.email.find_one(data)
            try:
                return dict_data["id"]
            except:
                return dict_data

    def read(self, *ids):
        # read - find data for input id
        list_dict = []
        for id in ids:
            if self.email.find_one({"id": id}):
                for find_data in self.email.find({"id": id}):
                    list_dict += [find_data]
        return list_dict

    def update(self, id=None, **new_data):
        # update - update documents
        data = {"id": id}
        if not id:
            return "Missing id"
        elif self.email.find_one(data):
            self.email.update_one(data, {"$set": new_data})
            return "Success"
        else:
            return "Denied"

    def delete(self, id=None):
        # delete - delete documents
        if not id:
            return "Missing data"
        if self.email.find_one({"id": id}):
            self.email.delete_one({"id": id})
            return "Success"
        else:
            return "Not found"

    def pop_100el(self):
        # get 100 last documents
        mass = []
        find_new = self.email.find({"time": {"$lt": time()}})
        for mail in find_new[:100]:
            mass += [mail]
            self.email.find_one_and_delete(mail)
        return mass

    def count(self, data=None):
        # get count documents for data
        return self.email.find(data).count()

    def show_db(self):
        # print all data from db(for debugging)
        for i in self.email.find():
            print(i)
