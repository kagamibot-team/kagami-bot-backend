from ..events.eventManager import EventManager
from .public import publicCommandEventManager


commandEventManager = EventManager({**publicCommandEventManager})
