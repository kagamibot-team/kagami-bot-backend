from nonebot.plugin import PluginMetadata


from .config import Config

# ACTIVATE ALL SUB MODULE
from . import catch

from .events import activateRoot, EventManager
from .commands import commandEventManager


root = EventManager({**commandEventManager})


activateRoot(root)


__plugin_meta__ = PluginMetadata(
    name="catch",
    description="",
    usage="",
    config=Config,
)
