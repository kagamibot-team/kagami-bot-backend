from dataclasses import dataclass


@dataclass
class PlayerDataChangedEvent:
    uid: int


@dataclass
class PlayerStorageChangedEvent(PlayerDataChangedEvent):
    aid: int
    count_delta: int
    count_from: int
    count_to: int


@dataclass
class PlayerMergeEvent(PlayerDataChangedEvent):
    uid: int
    aids: tuple[int, int, int]
    result: int
    is_succeed: bool
    count: int
