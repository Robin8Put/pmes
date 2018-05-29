from Parsing import Parsing_block, Table_new
from pprint import pprint

def run(from_i, to_i):
    for i in range(from_i, to_i):
        pars = Parsing_block(i)
        getblock = pars.get_transaction_in_block()
        get_raw_transaction = pars.get_raw_transaction()
        decode_raw_transaction = pars.decode_raw_transaction()
        if i%10 == 0:
            print(i)


if __name__ == "__main__":
    #2632167629
    #run(0, 144584)


#db = Table_new()
text = {"1": [{"fwre": 121,
             "qwe": 121
            }]
}
#db.insert("Qwerty24", **text)

