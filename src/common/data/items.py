import datetime

from pydantic import BaseModel

from src.base.exceptions import KagamiArgumentException, KagamiRangeError
from src.repositories.skin_repository import SkinData
from src.ui.types.common import AwardInfo, UserData


class UseItemArgs(BaseModel):
    count: int = 1
    target: UserData | None
    user: UserData
    use_time: datetime.datetime

    def require_count_range(self, n_min: int | None = None, n_max: int | None = None):
        if n_min is not None and self.count < n_min:
            raise KagamiRangeError("物品数量", f"至少为 {n_min}", self.count)
        if n_max is not None and self.count > n_max:
            raise KagamiRangeError("物品数量", f"不超过 {n_max}", self.count)

    def require_target(self, required: bool = True):
        if required and self.target is None:
            raise KagamiArgumentException("要指定一个人哦")
        elif not required and self.target is not None:
            raise KagamiArgumentException("不用指定目标哦")


class UseItemSkinPackEvent(BaseModel):
    uid: int
    args: UseItemArgs
    skin_data: SkinData
    remain: int
    biscuit_return: int
    biscuit_current: int
    do_user_have_before: bool
    award_info: AwardInfo
    all_skins_data: list[SkinData]
