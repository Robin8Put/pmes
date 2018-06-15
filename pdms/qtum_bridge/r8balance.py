from decimal import Decimal
from copy import copy


class R8Balance:
    def __init__(self, d, decimals=8):
        self.d = copy(d)
        self.decimals = decimals

        int_part, decimal_part = str(self.d).split('.')
        decimal_part = decimal_part[:8]

        self.balance = int_part + decimal_part
        self.balance = self.balance + '0'*(decimals - len(decimal_part))

    def get_balance(self):
        return self.balance


def main():
    b = R8Balance(Decimal('0.3678'), 8)
    b1 = R8Balance(Decimal('732320.332323232328'), 8)
    print(b1.get_balance())


if __name__ == '__main__':
    main()