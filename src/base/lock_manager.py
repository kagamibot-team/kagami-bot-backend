"""
This module contains the AsyncioLockManager class, which is used to manage locks for asyncio.
---
The module is completely writtened by CODEGEEX.
"""

import asyncio


class AsyncioLockManager:
    """A class that manages locks for asyncio"""

    locks: dict[str, asyncio.Lock]

    def __init__(self):
        self.locks = {}

    def get_lock(self, key: str):
        """Get a lock for a given key"""
        self.locks.setdefault(key, asyncio.Lock())
        return self.locks[key]

    _instance: "AsyncioLockManager | None" = None

    @classmethod
    def get(cls) -> "AsyncioLockManager":
        """Get the singleton instance of the lock manager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def get_lock(key: str) -> asyncio.Lock:
    """Get a lock for a given key"""
    return AsyncioLockManager.get().get_lock(key)


__all__ = ["AsyncioLockManager", "get_lock"]
