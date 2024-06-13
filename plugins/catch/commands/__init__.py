from ..events.manager import EventManager
from .public import publicCommandEventManager


commandEventManager = EventManager()

commandEventManager.merge(publicCommandEventManager)


__all__ = ["commandEventManager"]
