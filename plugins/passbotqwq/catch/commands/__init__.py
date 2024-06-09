from ...putils.command import CommandBase

from .basics import (
    Catch,
    CrazyCatch,
    CatchHelp,
    CatchStorage,
    CatchHangUpSkin,
    CatchDisplay,
    CatchFilterNoDescription,
    CatchProgress,
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
    CatchAdminObtainSkin,CatchAdminDeleteSkinOwnership
)


enabledCommand: list[CommandBase] = [
    Catch(),
    CrazyCatch(),
    CatchHelp(),
    CatchStorage(),
    CatchProgress(),
    CatchFilterNoDescription(),
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
]
