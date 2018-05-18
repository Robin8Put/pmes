from models import Table

# connect to db
db_news = Table("news", "News")
db_accounts = Table("news", "Accounts")


def set_news(**data):
    """
    Method take data and find id from db_account on public key. Insert data in db_news and update count in db_accounts
    param data: dict
    return: Ok or Error
    """
    try:
        if db_accounts.find({"public_key": data["public_key"]}):
            id = db_accounts.find({"public_key": data["public_key"]})
            data.pop("public_key")
            data["id"] = id
            db_news.insert_many_id(**data)
            db_accounts.update_inc(id, "count")
            return "Ok"
        else:
            return "Incorrect data"
    except:
        return "Missing public key"


def get_news(id=None):
    """
    Method take id and find count in db_account. 
    Return data in db_news and update count(count=0) in db_accounts
    param data: id
    return: list from dict: [{},{}] or Error
    """
    if id:
        try:
            count = db_accounts.read(id)[0]["count"]
        except:
            return []
        data = db_news.pop_news(id, count)
        db_accounts.update(id, **{"count": 0})
        return data
    else:
        return "Missing id"
