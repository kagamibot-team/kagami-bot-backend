"""
在群聊和控制台中都可以使用的命令
"""

from ...events.manager import EventManager
from .ping import pingManager
from .awards import awardManager


publicCommandEventManager = EventManager()
publicCommandEventManager.merge(pingManager)
publicCommandEventManager.merge(awardManager)
