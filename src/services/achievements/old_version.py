from src.common.dataclasses.game_events import (
    MergeEvent,
    UserDataUpdatedEvent,
    UserTryCatchEvent,
)
from src.core.unit_of_work import UnitOfWork

from .base import (
    AlwaysDisplayAchievement,
    DisplayWhenAchievedAchievement,
    NoPriseAchievement,
    register_achievement,
)


class AllOneStarAchievement(NoPriseAchievement, AlwaysDisplayAchievement):
    name: str = "七(一)星连珠"
    description: str = "嗯……一次性抽到七个一星！？"

    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, UserTryCatchEvent):
            return False
        if not event.successed:
            return False
        count = 0
        for r in event.results:
            if r.info.level.lid == 1:
                count += r.count
        return count >= 7


class NiceCatchAchievement(NoPriseAchievement, AlwaysDisplayAchievement):
    name: str = "欧皇附体"
    description: str = "一次抓到了两个四星（或者以上）"

    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, UserTryCatchEvent):
            return False
        if not event.successed:
            return False

        count = 0
        for r in event.results:
            if r.info.level.lid in (4, 5):
                count += r.count
        return count >= 2


class TimerAchievement(NoPriseAchievement, AlwaysDisplayAchievement):
    name: str = "读秒大师"
    description: str = "什么！剩余零秒？！"

    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, UserTryCatchEvent):
            return False
        return event.data.meta.need_time == "0秒"


class TripleAchivement(NoPriseAchievement, AlwaysDisplayAchievement):
    name: str = "三 小 哥"
    description: str = "一次抓到三个同一个小哥？"

    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, UserTryCatchEvent):
            return False
        if not event.successed:
            return False
        for r in event.results:
            if r.count >= 3:
                return True
        return False


class MergeTripleAchievement(DisplayWhenAchievedAchievement):
    name: str = "合成：三小哥"
    description: str = "用三个小哥合成三小哥。"
    prise_description: str | None = "50 薯片"

    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, MergeEvent):
            return False
        view = event.merge_view
        if (
            view.inputs[0].name == "小哥"
            and view.inputs[1].name == "小哥"
            and view.inputs[2].name == "小哥"
        ):
            if view.output.info.name == "三小哥":
                return True
        return False

    async def prise(self, uow: UnitOfWork, uid: int) -> None:
        await uow.money.add(uid, 50)


def register_old_version_achievements():
    register_achievement(AllOneStarAchievement())
    register_achievement(NiceCatchAchievement())
    register_achievement(TimerAchievement())
    register_achievement(TripleAchivement())
    register_achievement(MergeTripleAchievement())
