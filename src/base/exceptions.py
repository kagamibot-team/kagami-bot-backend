class ObjectNotFound(Exception):
    """当找不到某个对象时抛出此异常"""

    pass


class ObjectAlreadyExists(Exception):
    """当某个对象已经存在时抛出此异常"""

    pass
