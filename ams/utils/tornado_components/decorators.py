import os
import sys

def verify(func):
    async def wrapper(*args, **kwargs):
        import settings
        with open(os.path.join(settings.BASE_DIR, "keys.json")) as f:
            keys = json.load(f)

        pubkey = keys["pubkey"]

        message = kwargs.get("message")
        signature = kwargs.get("signature")
        try:
            flag = Qtum.verify_message(message, signature, pubkey)
        except:
            flag = None
        if not flag:
            result =  {"error":403, "reason":"Invalid signature"}
        else:
            result = await func(*args, **kwargs)
        return result
    return wrapper