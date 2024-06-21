from .loader import init
init()


# 暂时导入旧版的指令集，因为还需要使用。等旧版的指令都迁移完了就删掉这两行
from . import deprecated as _
