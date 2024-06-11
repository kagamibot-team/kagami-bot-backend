from nonebot.plugin import PluginMetadata


# IMPORT ALL SUB MODULES
from . import catch
from . import auto_reply
from .putils.config import Config


__plugin_meta__ = PluginMetadata(
    name="passbotqwq",
    description="",
    usage="",
    config=Config,
)
