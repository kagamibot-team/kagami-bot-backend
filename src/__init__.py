from nonebot.plugin import PluginMetadata

from .config import Config
from .events import activateRoot


# ACTIVATE ALL SUB MODULE
from . import catch as _
from .events import root

activateRoot(root)


__plugin_meta__ = PluginMetadata(
    name="catch",
    description="",
    usage="",
    config=Config,
)
