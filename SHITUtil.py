import itertools
import operator
import functools

def prng(x, a, c, m):
    while True:
        x = (a * x + c) % m
        yield x

def generateWEPKey(passphrase):
    bits = [0,0,0,0]
    for i, c in enumerate(passphrase):
        bits[i & 3] ^= ord(c)
    val = functools.reduce(operator.__or__, (b << 8*i for (i,b) in enumerate(bits)))
    keys = []
    for i, b in enumerate(itertools.islice(prng(val, 0x343fd, 0x269ec3, 1<<32), 20)):
        keys.append((b >> 16) & 0xff)
    return '%02x%02x%02x%02x%02x'.upper() % tuple(keys[:5])

