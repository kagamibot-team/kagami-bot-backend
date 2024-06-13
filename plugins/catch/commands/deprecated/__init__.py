"""
所有在 Onebot V11 协议下的指令
"""


from ..basics import CommandBase

from .basics import (
    Catch,
    CrazyCatch,
    CatchHelp,
    CatchStorage,
    CatchHangUpSkin,
    CatchDisplay,
    CatchProgress,
    CatchShop,
    CatchCheckMoney,
    CatchShowUpdate,
)

from .admin import (
    CatchAllAwards,
    CatchAllLevel,
    CatchSetInterval,
    CatchModify,
    CatchLevelModify,
    CatchRemoveAward,
    CatchCreateAward,
    CatchCreateLevel,
    Give,
    Clear,
    CatchAddSkin,
    CatchModifySkin,
    CatchAdminDisplay,
    CatchAdminObtainSkin,
    CatchAdminDeleteSkinOwnership,
    CatchResetEveryoneCacheCount,
    CatchAdminHelp,
    CatchGiveMoney,
    AddAltName,
    RemoveAltName,
    AddTags,
    RemoveTags,
)


enabledCommand: list[CommandBase] = [
    Catch(),
    CrazyCatch(),
    CatchHelp(),
    CatchStorage(),
    CatchProgress(),
    CatchDisplay(),
    CatchHangUpSkin(),
    CatchAllAwards(),
    CatchAllLevel(),
    CatchSetInterval(),
    CatchModify(),
    CatchLevelModify(),
    CatchRemoveAward(),
    CatchCreateAward(),
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
    CatchShowUpdate(),
    CatchAdminHelp(),
    CatchGiveMoney(),
    AddAltName(),
    RemoveAltName(),
    AddTags(),
    RemoveTags(),
]
