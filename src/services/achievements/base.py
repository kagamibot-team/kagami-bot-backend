import base64
from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.common.dataclasses.game_events import DummyEvent, UserDataUpdatedEvent
from src.core.unit_of_work import UnitOfWork


class Achievement(BaseModel, ABC):
    """
    最基础的成就
    """

    name: str
    description: str
    prise_description: str | None = None

    @property
    def flag(self) -> str:
        """用于记录用户是否达成成就的 Flag"""
        return f"flag_achievement_{base64.b64encode(self.name.encode()).decode()}"

    async def have_got(self, uow: UnitOfWork, uid: int) -> bool:
        """判断一个用户有没有拿到一个成就

        Args:
            uow (UnitOfWork): 工作单元
            uid (int): 用户 ID

        Returns:
            bool: 是否拿到了这个成就
        """

        return await uow.user_flag.have(uid, self.flag)

    @abstractmethod
    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        """判断一个人有没有达成成就的条件

        Args:
            uow (UnitOfWork): 工作单元
            event (UserDataUpdatedEvent): 更新时传递的事件

        Returns:
            bool: 是否达成了成就
        """

    @abstractmethod
    async def check_can_display(self, uow: UnitOfWork, uid: int) -> bool:
        """判断一个成就能不能被展示出来

        Args:
            uow (UnitOfWork): 工作单元
            uid (int): 用户 ID

        Returns:
            bool: 是否展示出来
        """

    @abstractmethod
    async def prise(self, uow: UnitOfWork, uid: int) -> None:
        """给一个玩家给予成就奖励

        Args:
            uow (UnitOfWork): 工作单元
            uid (int): 用户 ID
        """

    def __str__(self) -> str:
        msg = self.name + "\n    " + self.description
        if self.prise_description:
            msg += "\n    获得奖励：" + self.prise_description

        return msg


class NoPriseAchievement(Achievement):
    prise_description: str | None = None

    async def prise(self, uow: UnitOfWork, uid: int) -> None:
        return


class AlwaysDisplayAchievement(Achievement):
    async def check_can_display(self, uow: UnitOfWork, uid: int) -> bool:
        return True


class NeverDisplayAchievement(Achievement):
    async def check_can_display(self, uow: UnitOfWork, uid: int) -> bool:
        return False


class DisplayWhenAchievedAchievement(Achievement):
    async def check_can_display(self, uow: UnitOfWork, uid: int) -> bool:
        return await self.have_got(uow, uid)


class DummyAchievement(Achievement):
    """
    只能由 DummyEvent 触发的成就。这里的奖励还没有定义，需要子类再进行定义
    """

    dummy_data: str

    async def validate_achievement(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, DummyEvent):
            return False
        return event.data == self.dummy_data


class TestAchievement(DummyAchievement, NoPriseAchievement):
    """
    嗯这玩意是用于测试的，所以不给奖励
    """

    name: str = "测试成就"
    description: str = "测试成就的描述"
    dummy_data: str = "test_trigger"
    can_display: bool = False

    async def check_can_display(self, uow: UnitOfWork, uid: int) -> bool:
        return self.can_display


class AchievementService:
    achievements: list[Achievement]

    def __init__(self) -> None:
        self.achievements = []

    def register(self, achievement: Achievement):
        self.achievements.append(achievement)

    async def update(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> list[Achievement]:
        """一次成就更新，会自动结算成就奖励

        Args:
            uow (UnitOfWork): 工作单元
            event (UserDataUpdatedEvent): 事件

        Returns:
            list[BaseAchievement]: 在这次检查中达成的成就列表
        """
        achieved: list[Achievement] = []

        for a in self.achievements:
            if await a.have_got(uow, event.uid):
                continue
            if await a.validate_achievement(uow, event):
                await a.prise(uow, event.uid)
                await uow.user_flag.add(event.uid, a.flag)
                achieved.append(a)

        return achieved


service = AchievementService()


def get_achievement_service() -> AchievementService:
    """
    获得一个存有成就的服务
    """
    return service


def register_achievement(achievement: Achievement):
    """
    注册一个成就
    """
    service.register(achievement)
