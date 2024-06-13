from ..events.manager import EventManager
from .public import publicCommandEventManager
from .onebot import onebotEventManager


commandEventManager = EventManager()

commandEventManager.merge(publicCommandEventManager)
commandEventManager.merge(onebotEventManager)


__all__ = ["commandEventManager"]
