import time
from random import Random


def get_random():
    return Random(hash(f"{time.time()}"))
