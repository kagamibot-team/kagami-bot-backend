from pydantic import BaseModel

from .award import GotAwardDisplay, InfoView
from .user import UserData


class CatchMesssage(BaseModel):
    """
    抓小哥时的提示消息，可能没有抓到小哥
    """

    user: UserData
    "抓小哥的玩家"

    slot_remain: int
    "还有多少次抓小哥的次数"

    slot_sum: int
    "开了多少个槽位"

    next_time: float
    "下次槽位恢复的剩余时间"

    group_id: int | None
    "群号"

    pack_id: int
    "现在在哪个猎场"

    @property
    def timedelta_text(self):
        "倒计时"
        result = ""
        hours = int(self.next_time / 3600)
        minutes = int(self.next_time / 60) % 60
        seconds = int(self.next_time) % 60
        if hours > 0:
            result += f"{hours}小时"
        if hours > 0 or minutes > 0:
            result += f"{minutes}分钟"
        result += f"{seconds}秒"
        return result


class CatchResultMessage(CatchMesssage):
    """
    抓到小哥时的提示消息
    """

    money_changed: int
    "钱的变化数量"

    money_sum: int
    "在抓之后的总钱数"

    catchs: list[GotAwardDisplay]
    "抓小哥的条目"


class Catch(BaseModel):
    info: InfoView
    count: int
    is_new: bool


class SuccessfulCatchMeta(BaseModel):
    get_chip: int
    own_chip: int
    remain_time: int
    max_time: int
    need_time: str
    field_from: int


class SuccessfulCatch(BaseModel):
    name: str
    meta: SuccessfulCatchMeta
    catchs: list[Catch]

    @staticmethod
    def from_catch_result(data: CatchResultMessage):
        return SuccessfulCatch(
            name=data.user.name,
            meta=SuccessfulCatchMeta(
                get_chip=data.money_changed,
                own_chip=data.money_sum,
                remain_time=data.slot_remain,
                max_time=data.slot_sum,
                need_time=data.timedelta_text,
                field_from=data.pack_id,
            ),
            catchs=[
                Catch(
                    info=InfoView.from_award_info(d.info),
                    count=d.count,
                    is_new=d.is_new,
                )
                for d in data.catchs
            ],
        )
