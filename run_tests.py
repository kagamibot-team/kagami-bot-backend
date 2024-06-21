import nonebot
import unittest

nonebot.init(_env_file=(".env.test",))


from tests import *
import src as _


if __name__ == "__main__":
    unittest.main()
