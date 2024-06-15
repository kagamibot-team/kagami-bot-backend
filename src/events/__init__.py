"""
同样，这里也导入所有的子包
"""


import importlib
import os
import pathlib
import pkgutil


def _import(name: str, *parents: str) -> None:
    importlib.import_module('.'.join([__name__, *parents, name]))


def _walk(path: str, *parents: str) -> None:
    for _, name, _ in pkgutil.iter_modules([path]):
        _import(name, *parents)
    
    for subfolder in os.listdir(path):
        if os.path.isdir(os.path.join(path, subfolder)):
            _walk(os.path.join(path, subfolder), *parents, subfolder)


package_dir = pathlib.Path(__file__).resolve().parent
_walk(str(package_dir))
