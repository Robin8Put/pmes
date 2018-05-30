from Parsing import ParsingBlock, TableNew
from pprint import pprint


def run(from_i, to_i):
    for i in range(from_i, to_i):
        pars = ParsingBlock(i)
        getblock = pars.get_transaction_in_block()
        get_raw_transaction = pars.get_raw_transaction()
        decode_raw_transaction = pars.decode_raw_transaction()
        if i%10 == 0:
            print(i)


if __name__ == "__main__":
    # 2632167629
    run(0, 144584)
