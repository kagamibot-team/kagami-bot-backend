# 初始化事件监听
from .events import activateRoot
from .events import root

activateRoot(root)

# 导入 `commands` 模块，保证里面的事件监听被绑定
from . import commands

# 导入数据库有关的模型模块，保证能够被 SQLAlchemy 扫描到
from . import models

# 暂时导入旧版的指令集，因为还需要使用。等旧版的指令都迁移完了就删掉这两行
from . import catch as _


__all__ = ["root", "commands", "models"]
