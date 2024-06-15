# 初始化事件监听
from src.common.event_root import activateRoot, root

activateRoot(root)

# 导入 `commands` 模块和 `events` 模块，保证里面的事件监听被绑定
from . import commands
from . import events

# 暂时导入旧版的指令集，因为还需要使用。等旧版的指令都迁移完了就删掉这两行
from .commands import deprecated as _


__all__ = ["commands", "events"]
