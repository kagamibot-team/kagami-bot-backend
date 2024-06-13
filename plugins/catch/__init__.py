from nonebot.plugin import PluginMetadata

from .config import Config
from .events import activateRoot, EventManager
from .commands import commandEventManager


# ACTIVATE ALL SUB MODULE
from . import catch


root = EventManager()
root.merge(commandEventManager)

activateRoot(root)


__plugin_meta__ = PluginMetadata(
    name="catch",
    description="",
    usage="",
    config=Config,
)
