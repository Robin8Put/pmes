
import time
import settings


class Table(object):
    """Custom driver for writing data to mongodb
    By default database name is 'pmes',
             collection name is 'email'
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

        self.client = settings.SYNC_DB_CLIENT

        self.database = self.client[self.db_name]

        # Set collection nsme
        self.email = self.database[self.collection]

    def insert(self, id=None, **data):
        try:
            if id:
                data.update({"id": id})
                if self.email.find_one({"id": id}):
                    return "Denied"
                else:
                    self.email.insert_one(data).inserted_id
            else:
                self.email.insert_one(data).inserted_id
            return "Success"
        except:
            return "Failed"

    def find(self, data=None):
        if not data:
            return "Missing data"
        if self.email.find_one(data):
            dict_data = self.email.find_one(data)
            try:
                return dict_data["id"]
            except:
                return dict_data

    def read(self, *ids):
        list_dict = []
        for id in ids:
            if self.email.find_one({"id": id}):
                for i in self.email.find({"id": id}):
                    list_dict += [i]
        return list_dict

    def update(self, id=None, **new_data):
        data = {"id": id}
        if not id:
            return "Missing id"
        elif self.email.find_one(data):
            self.email.update_one(data, {"$set": new_data})
            return "Success"
        else:
            return "Denied"

    def delete(self, id=None):
        if not id:
            return "Missing data"
        if self.email.find_one({"id": id}):
            self.email.delete_one({"id": id})
            return "Success"
        else:
            return "Not found"

    def pop_100el(self):
        mass = []
        for i in self.email.find({"time": {"$lt": time.time()}})[:100]:
            mass += [i]
            self.email.find_one_and_delete(i)
        return mass

    def count(self, data=None):
        return self.email.find(data).count()

    def show_db(self):
        for i in self.email.find():
            print(i)
