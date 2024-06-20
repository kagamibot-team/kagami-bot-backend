import asyncio
import importlib
import os
import pathlib
import pkgutil
from types import ModuleType

from nonebot import get_driver, logger
from src.base.event_root import activateRoot, root


loaded_modules: list[ModuleType] = []
to_load_parents = (
    ("components",),
    ("commands", "console"),
    ("commands", "onebot"),
    ("commands", "public"),
    ("events",),
    ("logic",),
)


def _import(name: str, *parents: str):
    _name = ".".join(["src", *parents, name])
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
    for to_import in to_load_parents:
        loaded_modules.extend(
            _walk_load(os.path.join(package_dir, *to_import), *to_import)
        )
    logger.info("载入完成，一共载入了%d个模块" % len(loaded_modules))


def reload():
    root.clear()
    for p in loaded_modules:
        try:
            importlib.reload(p)
        except Exception as e:
            logger.error(f"重载模块 {p.__name__} 失败，原因：{e}")
    logger.info("重载了%d个模块" % len(loaded_modules))

    loaded_modules.clear()
    load_packages()


def _tree():
    _tr: set[tuple[str, str]] = set()
    package_dir = pathlib.Path(__file__).resolve().parent

    for pa in to_load_parents:
        base = os.path.join(package_dir, *pa)

        for root, _, files in os.walk(base):
            for file in files:
                if file.endswith(".py"):
                    # 获取文件内容的 Hash 值
                    with open(os.path.join(root, file), "rb") as f:
                        _tr.add((os.path.join(root, file), f.read().hex()))

    return _tr


async def watchdog():
    last_tree = _tree()
    while True:
        await asyncio.sleep(1)
        new_tree = _tree()
        if new_tree != last_tree:
            logger.info("检测到文件变化，重新加载")
            reload()
            last_tree = new_tree


driver = get_driver()


@driver.on_startup
async def _():
    if driver.env == "dev":
        logger.info("在开发者模式下，会自动重载文件")
        asyncio.create_task(watchdog())


def init():
    activateRoot(root)
    load_packages()
