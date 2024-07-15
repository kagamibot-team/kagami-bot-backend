from pydantic import BaseModel

from src.views.user import UserData

from .award import AwardInfo


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
    "下次槽位恢复的时间"

    group_id: int | None
    "群号"

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

    catchs: list[AwardInfo]
    "抓小哥的条目"

    @property
    def title(self):
        "标题"
        return self.user.name + " 的一抓"

    @property
    def details(self):
        "标题下方的文字"
        return (
            f"本次获得{self.money_changed}薯片，"
            f"目前共有{self.money_sum}薯片。\n"
            f"剩余次数：{self.slot_remain}/{self.slot_sum}，"
            f"距下次次数恢复还要{self.timedelta_text}"
        )
