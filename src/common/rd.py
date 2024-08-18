import os
from random import Random


def get_random():
    return Random(os.urandom(16))
