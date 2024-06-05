from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata


from .config import Config


# IMPORT ALL SUB MODULES
from . import catch
from . import auto_reply


__plugin_meta__ = PluginMetadata(
    name="passbotqwq",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


