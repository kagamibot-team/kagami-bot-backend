"""
在群聊和控制台中都可以使用的命令
"""

from ...events.manager import EventManager
from .common import *


publicCommandEventManager = EventManager({**pingManager})
