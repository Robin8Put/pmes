from time import time
import random

def t():
    data = []
    for i in range(0, 10):
        i = random.randint(1000, 10000)
        f = random.random()
        data.append((i, f))

    print(data)

    for i, f in data:
        print(i*f)


if __name__ == '__main__':
    t()