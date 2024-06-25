import importlib
import os
import pathlib
import pkgutil
import unittest
from types import ModuleType

import nonebot
from nonebot.adapters.console.adapter import Adapter as ConsoleAdapter
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter


# 初始化 Nonebot 环境
nonebot.init(
    _env_file=(),
    sqlalchemy_database_url="sqlite+aiosqlite:///:memory:",
    enable_white_list=True,
    white_list_groups=[1, 2],
    admin_id=3,
    admin_groups=[1],
    custom_replies={"4": "a"},
    my_name=["小镜"],
)

driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)  # type: ignore
driver.register_adapter(ConsoleAdapter)  # type: ignore

import src as _


# 导入所有的测试用例
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
