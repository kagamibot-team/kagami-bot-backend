import importlib
import os
import pathlib
import pkgutil
from types import ModuleType
import nonebot
import unittest

nonebot.init(_env_file=(".env.test",))

import src as _


def _import(name: str, *parents: str):
    nonebot.logger.info(f"importing {name}")
    _name = ".".join([*parents, name])
    m = importlib.import_module(_name)
    return m


def _walk_load(path: str, *parents: str) -> list[ModuleType]:
    mds: list[ModuleType] = []

    for _, name, _ in pkgutil.iter_modules([path]):
        mds.append(_import(name, *parents))

    for subfolder in os.listdir(path):
        if os.path.isdir(os.path.join(path, subfolder)):
            mds += _walk_load(os.path.join(path, subfolder), *parents, subfolder)

    return mds


def load_packages():
    package_dir = pathlib.Path(__file__).resolve().parent
    return _walk_load(os.path.join(package_dir, "tests"), "tests")


if __name__ == "__main__":
    modules = load_packages()

    suites = [unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules]
    unittest.TextTestRunner().run(unittest.TestSuite(suites))
