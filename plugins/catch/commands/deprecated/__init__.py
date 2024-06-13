"""
所有在 Onebot V11 协议下的指令
"""


from ..basics import CommandBase

from .basics import (
    CatchStorage,
    CatchHangUpSkin,
    CatchDisplay,
    CatchProgress,
    CatchShop,
    CatchCheckMoney,
)

from .admin import (
    CatchAllAwards,
    CatchAllLevel,
    CatchSetInterval,
    CatchModify,
    CatchLevelModify,
    CatchCreateLevel,
    Give,
    Clear,
    CatchAddSkin,
    CatchModifySkin,
    CatchAdminDisplay,
    CatchAdminObtainSkin,
    CatchAdminDeleteSkinOwnership,
    CatchResetEveryoneCacheCount,
    CatchGiveMoney,
    AddAltName,
    RemoveAltName,
    AddTags,
    RemoveTags,
)


enabledCommand: list[CommandBase] = [
    CatchStorage(),
    CatchProgress(),
    CatchDisplay(),
    # CatchHangUpSkin(),
    CatchAllAwards(),
    CatchAllLevel(),
    CatchSetInterval(),
    CatchModify(),
    CatchLevelModify(),
    CatchCreateLevel(),
    Give(),
    Clear(),
    CatchAddSkin(),
    CatchModifySkin(),
    CatchAdminDisplay(),
    CatchAdminObtainSkin(),
    CatchAdminDeleteSkinOwnership(),
    CatchShop(),
    CatchResetEveryoneCacheCount(),
    CatchCheckMoney(),
    CatchGiveMoney(),
    AddAltName(),
    RemoveAltName(),
    AddTags(),
    RemoveTags(),
]
