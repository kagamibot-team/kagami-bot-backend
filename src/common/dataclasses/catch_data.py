from dataclasses import dataclass


@dataclass()
class Pick:
    """
    抓小哥的单个结果
    """

    awardId: int
    awardName: str
    countBefore: int
    countDelta: int
    money: float


@dataclass()
class PickResult:
    picks: list[Pick]
    uid: int
    restPickCount: int
    maxPickCount: int
    timeToNextPick: float
    pickInterval: float

    moneyAfterPick: float

    extraMessages: list[str]
