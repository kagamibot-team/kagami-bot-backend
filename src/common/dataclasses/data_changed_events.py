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
