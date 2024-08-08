from enum import Enum
from pathlib import Path
from random import Random

from pydantic import BaseModel

from .award import AwardInfo, GotAwardDisplay
from .user import UserData


class MergeStatus(Enum):
    success = "成功！"
    fail = "失败！"
    what = "失败？"


class MokieImage(Enum):
    """
    榆木华摆出了一副什么表情……？
    """

    normal = "通常"
    laugh = "滑稽"
    astonish = "惊讶"
    xiaoge = "小哥"
    wtf = "黑化"

    @property
    def image_url(self) -> Path:
        return Path(f"./res/mokie/榆木华 表情 {self.value}.png")


class MokieMessage(BaseModel):
    """
    来看看这次合成，榆木华说了啥
    """

    text: str
    image: MokieImage


MOKIE_MESSAGE_FALLBACK = MokieMessage(text="", image=MokieImage.normal)

MOKIE_MESSAGES: dict[int, dict[int, tuple[MokieMessage, ...]]] = {
    1: {
        1: (
            MokieMessage(text="刚抓的小哥，便宜造！", image=MokieImage.normal),
            MokieMessage(text="嗯。", image=MokieImage.normal),
        ),
        2: (
            MokieMessage(text="可以，至少升了。", image=MokieImage.normal),
            MokieMessage(text="说不定破产以后要用。", image=MokieImage.normal),
        ),
        3: (
            MokieMessage(text="哦哦有点好。", image=MokieImage.normal),
            MokieMessage(text="实用配方！", image=MokieImage.normal),
        ),
        4: (
            MokieMessage(text="厉害啊。", image=MokieImage.normal),
            MokieMessage(text="给你赚到了。", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="你牛逼。", image=MokieImage.normal),
            MokieMessage(text="求送我。", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="嗯こ。", image=MokieImage.normal),
            MokieMessage(text="就这点薯片你想怎样？", image=MokieImage.normal),
        ),
    },
    2: {
        1: (
            MokieMessage(text="不如粑粑。", image=MokieImage.normal),
            MokieMessage(text="还有必要记配方吗？", image=MokieImage.normal),
        ),
        2: (
            MokieMessage(
                text="希望不要落到需要用这个配方的时候。", image=MokieImage.normal
            ),
            MokieMessage(text="一般般。", image=MokieImage.normal),
        ),
        3: (
            MokieMessage(text="没记的话记一下吧。", image=MokieImage.normal),
            MokieMessage(text="以后绝对用得到的。", image=MokieImage.normal),
        ),
        4: (
            MokieMessage(text="好好好。", image=MokieImage.normal),
            MokieMessage(text="狠狠跳步喽！", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="我也想要。", image=MokieImage.normal),
            MokieMessage(text="恭喜你啊。（咬牙切齿）", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="没亏多少。", image=MokieImage.normal),
            MokieMessage(text="下次一定！", image=MokieImage.normal),
        ),
    },
    3: {
        2: (
            MokieMessage(text="下次别合了。", image=MokieImage.normal),
            MokieMessage(text="吃一堑，长一智。", image=MokieImage.normal),
        ),
        3: (
            MokieMessage(text="感觉作用有限，配方。", image=MokieImage.normal),
            MokieMessage(text="今天天气不错。", image=MokieImage.normal),
        ),
        4: (
            MokieMessage(text="能用。", image=MokieImage.normal),
            MokieMessage(text="算是成功了吧。", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="还不错哦。", image=MokieImage.normal),
            MokieMessage(text="小赚！", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="胜败乃兵家常事！", image=MokieImage.normal),
            MokieMessage(text="我以前死在这过很多次。", image=MokieImage.normal),
        ),
    },
    4: {
        3: (
            MokieMessage(text="不好。", image=MokieImage.normal),
            MokieMessage(text="亏了。", image=MokieImage.normal),
        ),
        4: (
            MokieMessage(text="也行。", image=MokieImage.normal),
            MokieMessage(text="还可以。", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="一分耕耘一分收获吧。", image=MokieImage.normal),
            MokieMessage(text="不经历风雨，怎能见彩虹？", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="必要的牺牲。", image=MokieImage.normal),
            MokieMessage(text="其实不要的可以给我。", image=MokieImage.normal),
        ),
    },
    5: {
        4: (
            MokieMessage(
                text="万不得已的时候我也用过这种配方。", image=MokieImage.normal
            ),
            MokieMessage(text="嘛，回来个四星也行吧。", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="看得我胆战心惊的。", image=MokieImage.normal),
            MokieMessage(text="大手笔啊。", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="没必要。", image=MokieImage.normal),
            MokieMessage(text="自己留着点吧。", image=MokieImage.normal),
        ),
    },
    0: {
        0: (
            MokieMessage(text="这是什么？合一下。", image=MokieImage.normal),
            MokieMessage(text="唉。", image=MokieImage.normal),
        ),
    },
}

MOKIE_MESSAGES_XIAOHUA = (
    MokieMessage(text="像我吧。", image=MokieImage.normal),
    MokieMessage(text="哎这些东西真不知道哪来的。", image=MokieImage.normal),
)
"小华"

MOKIE_MESSAGES_LOVE = (
    MokieMessage(text="送我送我送我送我送我。", image=MokieImage.normal),
    MokieMessage(text="喜欢。", image=MokieImage.normal),
)
"榆木华厨的"

MOKIE_MESSAGES_ZERO = (MokieMessage(text="...", image=MokieImage.wtf),)
"合成了隐藏的小哥？！"


class MergeResult(BaseModel):
    """
    合成小哥时的消息
    """

    user: UserData
    successed: MergeStatus
    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    output: GotAwardDisplay
    cost_money: int
    remain_money: int
    merge_time: float

    @property
    def title1(self):
        return f"{self.user.name} 的合成材料："

    @property
    def title2(self):
        return f"合成结果：{self.successed.value}"

    @property
    def title3(self):
        return f"本次合成花费了你 {self.cost_money} 薯片，你还有 {self.remain_money} 薯片。"

    @property
    def input_highest_level(self):
        return max((i.level.lid for i in self.inputs))

    @property
    def result_level(self):
        return self.output.info.level.lid

    @property
    def is_shit(self):
        "合成的是粑粑小哥么"
        return self.output.info.aid == 89

    @property
    def random(self):
        return Random(hash(self.merge_time))

    @property
    def ymh_message(self) -> MokieMessage:
        if self.result_level == 0 and not self.is_shit:
            return self.random.choice(MOKIE_MESSAGES_ZERO)

        if self.output.info.aid == 9:
            # 小华
            return self.random.choice(MOKIE_MESSAGES_XIAOHUA)

        if self.output.info.aid in (34, 98):
            # 小水瓶子和小可怜
            return self.random.choice(MOKIE_MESSAGES_LOVE)

        _ms = MOKIE_MESSAGES.get(self.input_highest_level, {})
        _msls = _ms.get(self.result_level, ())

        if len(_msls) == 0:
            return MOKIE_MESSAGE_FALLBACK

        return self.random.choice(_msls)


class MergeHistory(BaseModel):
    """
    合成小哥的历史记录
    """

    inputs: tuple[AwardInfo, AwardInfo, AwardInfo]
    "用于合成的小哥"

    output: AwardInfo
    "合成结果"

    found_person: UserData
    "发现这个配方的人"


class MergeHistoryList(BaseModel):
    """
    合成小哥的历史记录列表
    """

    history: list[MergeHistory]
    "合成小哥的历史记录"
