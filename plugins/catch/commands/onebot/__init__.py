"""
所有仅在 QQ 答复的命令
"""


from ...events.manager import EventManager

from .public import publicEventManager


onebotEventManager = EventManager()
onebotEventManager.merge(publicEventManager)
