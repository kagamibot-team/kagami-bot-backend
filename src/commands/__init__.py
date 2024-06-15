"""
卧槽了，居然可以自动导入所有子包，终于不用费劲写 __init__.py 了，太好
"""


import importlib
import os
import pathlib
import pkgutil


to_walk = ('console', 'public', 'onebot')


def _import(name: str, *parents: str) -> None:
    importlib.import_module('.'.join([__name__, *parents, name]))


def _walk(path: str, *parents: str) -> None:
    for _, name, _ in pkgutil.iter_modules([path]):
        _import(name, *parents)
    
    for subfolder in os.listdir(path):
        if os.path.isdir(os.path.join(path, subfolder)):
            _walk(os.path.join(path, subfolder), *parents, subfolder)


for parent in to_walk:
    package_dir = pathlib.Path(__file__).resolve().parent
    _walk(os.path.join(package_dir, parent), parent)
