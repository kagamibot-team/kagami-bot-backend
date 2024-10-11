import base64
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, computed_field

from src.base.resources import Resource, static_res
from src.common.dataclasses.game_events import DummyEvent, UserDataUpdatedEvent
from src.core.unit_of_work import UnitOfWork


class AchievementType(Enum):
    """
    成就的类型，只会影响视图
    """

    advancement = 1
    "进度，比较像谁都可以达到的类型，例如游玩的里程碑"

    goal = 2
    "目标，可以努努力达到的类型，而且不一定是必须要达到的"

    challenge = 3
    "挑战，需要凹才能做到的事情"


class DisplayRule(Enum):
    """
    显示成就有哪些条件
    """

    always_display = 1
    "一直展示的成就，反正就是会出现在成就的清单中"

    blur_until_achieve = 2
    """
    在达成之前就显示在成就清单中，但是会模糊图标，只有成就名字，
    而成就的描述需要被隐藏。
    """

    hide_until_achieve = 3
    "在达成之前不会展示"

    always_hide = 4
    "一直隐藏，永远不会展示出来"


class AnnounceRule(Enum):
    """
    告知成就的方式
    """

    ## 算了，不要这个，感觉没有情景会用到
    # broadcast = 1
    # "开大喇叭广播给所有人，请谨慎使用"

    default = 0
    "在上一次对方输入指令的地方告知他人"

    no_announcement = -1
    "不告知"


class Achievement(BaseModel, ABC):
    """
    最基础的成就。这里是成就的元数据。
    """

    name: str
    "成就的名字，简短有力"

    description: str
    "成就的描述，比较短，但能够说明怎么达成这个成就"

    prise_description: str | None = None
    "奖励的描述，如果为 None 代表没有奖励"

    image: Resource = static_res("blank_placeholder.png")
    "成就的图标"

    achievement_type: AchievementType = AchievementType.advancement
    "成就的类型，只影响成就的视图"

    display_rule: DisplayRule = DisplayRule.always_display
    "成就的显示规则"

    announce_rule: AnnounceRule = AnnounceRule.default
    "成就的广播规则"

    @computed_field
    @property
    def image_url(self) -> str:
        return self.image.compress_image().url

    @property
    def image_path(self) -> Path:
        return self.image.path

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
    async def is_achievement_completed(
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


class DummyAchievement(Achievement):
    """
    只能由 DummyEvent 触发的成就。这里的奖励还没有定义，需要子类再进行定义
    """

    dummy_data: str

    async def is_achievement_completed(
        self, uow: UnitOfWork, event: UserDataUpdatedEvent
    ) -> bool:
        if not isinstance(event, DummyEvent):
            return False
        return event.data == self.dummy_data


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
            if await a.is_achievement_completed(uow, event):
                await a.prise(uow, event.uid)
                await uow.user_flag.add(event.uid, a.flag)
                achieved.append(a)

        return achieved


service = AchievementService()


def get_achievement_service() -> AchievementService:
    """
    获得当前 App 正在运行的成就服务
    """
    return service


def register_achievement(achievement: Achievement):
    """
    注册一个成就
    """
    get_achievement_service().register(achievement)
