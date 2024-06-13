from ..events.manager import EventManager
from .public import publicCommandEventManager


commandEventManager = EventManager({**publicCommandEventManager})
