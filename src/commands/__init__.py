"""
卧槽了，居然可以自动导入所有子包，终于不用费劲写 __init__.py 了，太好
"""


import importlib
import os
import pathlib
import pkgutil
from types import ModuleType


to_walk = ('console', 'public', 'onebot')


_modules: list[ModuleType] = []


def _import(name: str, *parents: str):
    return importlib.import_module('.'.join([__name__, *parents, name]))


def _walk(path: str, *parents: str) -> list[ModuleType]:
    mds: list[ModuleType] = []

    for _, name, _ in pkgutil.iter_modules([path]):
        mds.append(_import(name, *parents))
    
    for subfolder in os.listdir(path):
        if os.path.isdir(os.path.join(path, subfolder)):
            mds += _walk(os.path.join(path, subfolder), *parents, subfolder)

    return mds


def walk():
    global _modules

    for parent in to_walk:
        package_dir = pathlib.Path(__file__).resolve().parent
        _modules = _walk(os.path.join(package_dir, parent), parent)


walk()
