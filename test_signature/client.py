import json
import requests
import random
import pprint
import os
import sys

from bip32keys.bip32keys import Bip32Keys


def post_user():

    # Get public and private keys pair from file
    with open("generated.json") as keys:
        keys_list = json.load(keys)
    users_keys = random.choice(keys_list)

    public_key = users_keys["public_key"]
    private_key = users_keys["private_key"]

    print(f"Your private keys is: {public_key}")
    print(f"Your public key is: {private_key}")
    
    # Create message and dump the one to the json
    message = {
                "email": "test@test.com", 
                "phone": "123756349", 
                "timestamp": "1535646214275"
            }

    print("\nYour message is: ")
    print(message)
    print("\n")
        
    data = {
        "signature": Bip32Keys.sign_message(json.dumps(message), private_key),
        "public_key": public_key,
        "message":message
    }

    create_account_url = f"http://pdms2.robin8.io/api/accounts/"

    print(create_account_url)
    # Request to the server
    response = requests.post(create_account_url, data=json.dumps(data))

    print(response.json())



if __name__ == '__main__':
    folder = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(folder)
    post_user()

