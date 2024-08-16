from pydantic import BaseModel

from src.models.level import Level

from .award import AwardInfo, GotAwardDisplay
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

    @property
    def title(self):
        "标题"
        lmt = f"[{self.pack_id}号猎场]"
        if self.pack_id == 1:
            lmt = ""
        return lmt + self.user.name + " 的一抓"

    @property
    def details(self):
        "标题下方的文字"
        return (
            f"本次获得{self.money_changed}薯片，"
            f"目前共有{self.money_sum}薯片。\n"
            f"剩余次数：{self.slot_remain}/{self.slot_sum}，"
            f"距下次次数恢复还要{self.timedelta_text}"
        )


class LevelView(BaseModel):
    display_name: str
    color: str

    @staticmethod
    def from_model(lv: Level) -> "LevelView":
        return LevelView(
            display_name=lv.display_name,
            color=lv.color,
        )


class Info(BaseModel):
    description: str
    display_name: str
    color: str
    image: str
    level: LevelView

    @staticmethod
    def from_award_info(info: AwardInfo) -> "Info":
        return Info(
            description=info.description,
            display_name=info.name,
            color=info.color,
            image=info.image_url,
            level=LevelView.from_model(info.level),
        )


class Catch(BaseModel):
    info: Info
    count: int
    is_new: bool


class SuccessfulCatchMeta(BaseModel):
    get_chip: int
    own_chip: int
    remain_time: int
    need_time: str


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
                need_time=data.timedelta_text,
            ),
            catchs=[
                Catch(
                    info=Info.from_award_info(d.info),
                    count=d.count,
                    is_new=d.is_new,
                )
                for d in data.catchs
            ],
        )
