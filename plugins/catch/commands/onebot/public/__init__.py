from ....events.manager import EventManager
from .catch import catchEventManager


publicEventManager = EventManager()
publicEventManager.merge(catchEventManager)
