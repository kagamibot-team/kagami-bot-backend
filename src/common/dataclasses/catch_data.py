from pydantic import BaseModel


class Pick(BaseModel):
    """
    单条抓小哥的记录
    """

    beforeStats: int
    delta: int
    level: int


class Picks(BaseModel):
    """
    一个记录抓小哥结果的数据类，仅储存在内存中，可以在后续流程中更改其中的结果。
    """

    awards: dict[int, Pick]
    money: float
    uid: int
