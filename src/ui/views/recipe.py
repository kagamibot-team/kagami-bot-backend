from enum import Enum
from random import Random

from pydantic import BaseModel

from src.ui.views.catch import Catch, InfoView

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
    funny = "滑稽"
    astonish = "惊讶"
    xiaoge = "小哥"
    wtf = "黑化"
    laugh = "嘲讽"
    jealous = "咬牙切齿"
    shy = "心虚"
    afraid = "惶恐"


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
            MokieMessage(text="很经常的结果。", image=MokieImage.normal),
            MokieMessage(text="多试试吧，别的配方。", image=MokieImage.normal),
        ),
        2: (
            MokieMessage(text="可以，至少升了。", image=MokieImage.normal),
            MokieMessage(text="说不定破产以后要用。", image=MokieImage.normal),
            MokieMessage(text="不亏啊。", image=MokieImage.normal),
            MokieMessage(text="也算三个臭皮匠吧。", image=MokieImage.normal),
        ),
        3: (
            MokieMessage(text="哦哦有点好。", image=MokieImage.astonish),
            MokieMessage(text="实用配方！", image=MokieImage.normal),
            MokieMessage(text="其实有点难得。", image=MokieImage.normal),
            MokieMessage(text="好好记着哦。", image=MokieImage.normal),
        ),
        4: (
            MokieMessage(text="厉害啊。", image=MokieImage.astonish),
            MokieMessage(text="给你赚到了。", image=MokieImage.jealous),
            MokieMessage(text="我也记记。", image=MokieImage.astonish),
            MokieMessage(text="开抄！", image=MokieImage.laugh),
        ),
        5: (
            MokieMessage(text="你牛逼。", image=MokieImage.jealous),
            MokieMessage(text="求送我。", image=MokieImage.normal),
            MokieMessage(text="这么强？！", image=MokieImage.astonish),
            MokieMessage(text="你是怎么办到的！？", image=MokieImage.xiaoge),
        ),
        0: (
            MokieMessage(text="嗯こ。", image=MokieImage.laugh),
            MokieMessage(text="就这点薯片你想怎样？", image=MokieImage.laugh),
            MokieMessage(text="收徒。", image=MokieImage.laugh),
            MokieMessage(text="啦啦啦。", image=MokieImage.normal),
        ),
    },
    2: {
        1: (
            MokieMessage(text="不如粑粑。", image=MokieImage.normal),
            MokieMessage(text="还有必要记配方吗？", image=MokieImage.laugh),
            MokieMessage(text="别吧兄弟。", image=MokieImage.normal),
            MokieMessage(text="记得避雷。", image=MokieImage.normal),
        ),
        2: (
            MokieMessage(
                text="希望不要落到需要用这个配方的时候。", image=MokieImage.normal
            ),
            MokieMessage(text="一般般。", image=MokieImage.normal),
            MokieMessage(text="好无聊——", image=MokieImage.normal),
            MokieMessage(text="也行吧。", image=MokieImage.normal),
        ),
        3: (
            MokieMessage(text="没记的话记一下吧。", image=MokieImage.normal),
            MokieMessage(text="以后绝对用得到的。", image=MokieImage.normal),
            MokieMessage(text="收集度上去后很常用哦。", image=MokieImage.normal),
            MokieMessage(text="不要忽视这种配方。", image=MokieImage.normal),
        ),
        4: (
            MokieMessage(text="好好好。", image=MokieImage.normal),
            MokieMessage(text="狠狠跳步喽！", image=MokieImage.normal),
            MokieMessage(text="帅！", image=MokieImage.normal),
            MokieMessage(text="这个可以有！", image=MokieImage.astonish),
        ),
        5: (
            MokieMessage(text="我也想要啊。", image=MokieImage.astonish),
            MokieMessage(text="大家一起来抄吧！", image=MokieImage.normal),
            MokieMessage(text="恭喜你啊。", image=MokieImage.jealous),
            MokieMessage(text="也就成功升了三级而已。", image=MokieImage.jealous),
        ),
        0: (
            MokieMessage(text="还好没亏多少。", image=MokieImage.laugh),
            MokieMessage(text="不关我事哦。", image=MokieImage.shy),
            MokieMessage(text="下次一定！", image=MokieImage.normal),
            MokieMessage(text="多合合吧。", image=MokieImage.normal),
        ),
    },
    3: {
        2: (
            MokieMessage(text="下次不用合这个了。", image=MokieImage.laugh),
            MokieMessage(text="吃一堑，长一智。", image=MokieImage.normal),
            MokieMessage(text="嘛，总是会遇到的啦。", image=MokieImage.laugh),
            MokieMessage(text="知道了就可以避免了啦。", image=MokieImage.normal),
        ),
        3: (
            MokieMessage(text="感觉作用有限，配方。", image=MokieImage.normal),
            MokieMessage(text="今天天气不错。", image=MokieImage.normal),
            MokieMessage(text="好没槽点的配方！", image=MokieImage.normal),
            MokieMessage(text="那咋了？（学小人机）", image=MokieImage.xiaoge),
        ),
        4: (
            MokieMessage(text="蛮好用的。", image=MokieImage.normal),
            MokieMessage(text="算是成功了吧。", image=MokieImage.normal),
            MokieMessage(text="没成本更低的就用这种吧。", image=MokieImage.normal),
            MokieMessage(text="也不算少见。", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="还不错哦。", image=MokieImage.astonish),
            MokieMessage(text="小赚！", image=MokieImage.astonish),
            MokieMessage(text="多来点！", image=MokieImage.astonish),
            MokieMessage(text="我：有点东西", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="胜败乃兵家常事！", image=MokieImage.laugh),
            MokieMessage(text="我以前在这绊倒过很多次。", image=MokieImage.normal),
            MokieMessage(text="小华不知道哦。", image=MokieImage.normal),
            MokieMessage(text="别怪我，怪机器。", image=MokieImage.shy),
        ),
    },
    4: {
        3: (
            MokieMessage(text="亏。", image=MokieImage.laugh),
            MokieMessage(text="亏了。", image=MokieImage.laugh),
            MokieMessage(text="多亏了你。", image=MokieImage.laugh),
            MokieMessage(text="多亏了，你？", image=MokieImage.laugh),
        ),
        4: (
            MokieMessage(text="也行……？", image=MokieImage.normal),
            MokieMessage(text="还可以。", image=MokieImage.normal),
            MokieMessage(text="说不定可以换换口味。", image=MokieImage.normal),
            MokieMessage(text="这是你需要的吗？", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="确实是有付出才有收获。", image=MokieImage.normal),
            MokieMessage(text="不经历风雨，怎能见彩虹？……好土。", image=MokieImage.normal),
            MokieMessage(text="升星的钱你来出！", image=MokieImage.normal),
            MokieMessage(text="挺敢的嘛！（不说你很勇嘛）", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="必要的牺牲。", image=MokieImage.laugh),
            MokieMessage(text="其实不要的可以给我。", image=MokieImage.laugh),
            MokieMessage(
                text="其实就算你多扔进去几个四星，成功率也不会提高很多，貌似，我猜的。",
                image=MokieImage.shy,
            ),
            MokieMessage(text="噗。", image=MokieImage.laugh),
        ),
    },
    5: {
        4: (
            MokieMessage(
                text="万不得已的时候我也用过这种配方。", image=MokieImage.normal
            ),
            MokieMessage(text="嘛，回来个四星也行吧。", image=MokieImage.normal),
            MokieMessage(
                text="看你抱着他们过来的时候都有点吓人！", image=MokieImage.shy
            ),
            MokieMessage(text="追求稳定性吗。", image=MokieImage.normal),
        ),
        5: (
            MokieMessage(text="看得我胆战心惊的。还好出货了。", image=MokieImage.shy),
            MokieMessage(text="大手笔啊。", image=MokieImage.astonish),
            MokieMessage(text="你是真馋了。", image=MokieImage.normal),
            MokieMessage(text="也没啥好惊讶的，好像。", image=MokieImage.normal),
        ),
        0: (
            MokieMessage(text="没必要。", image=MokieImage.laugh),
            MokieMessage(text="自己留着点吧。", image=MokieImage.laugh),
            MokieMessage(
                text="虽然没人权但是也不能这样造他们啊。", image=MokieImage.shy
            ),
            MokieMessage(text="无聊和我找话吗。", image=MokieImage.laugh),
        ),
    },
    0: {
        0: (
            MokieMessage(text="这是什么？合一下。", image=MokieImage.laugh),
            MokieMessage(text="唉。", image=MokieImage.laugh),
            MokieMessage(text="你花这些薯片是为了什么呢……", image=MokieImage.laugh),
            MokieMessage(text="别看我，是机器干掉的。", image=MokieImage.shy),
        ),
    },
}

MOKIE_MESSAGES_XIAOHUA = (
    MokieMessage(text="像我吧。", image=MokieImage.xiaoge),
    MokieMessage(text="哎，这些东西真不知道哪来的。", image=MokieImage.normal),
    MokieMessage(text="虽然不是我，但别想什么奇怪的事。", image=MokieImage.shy),
    MokieMessage(text="看到这个的时候，他们会想起我吗……", image=MokieImage.normal),
)
"小华"

MOKIE_MESSAGES_LOVE = (
    MokieMessage(text="捏。", image=MokieImage.normal),
    MokieMessage(text="可爱。", image=MokieImage.normal),
    MokieMessage(text="收着吧。", image=MokieImage.normal),
    MokieMessage(text="看不腻呀。", image=MokieImage.normal),
    MokieMessage(text="单纯很喜欢。", image=MokieImage.normal),
    MokieMessage(text="偷偷吸了一口。", image=MokieImage.normal),
    MokieMessage(text="请保护好他们哦。", image=MokieImage.normal),
    MokieMessage(text="软软的，很想欺负。", image=MokieImage.normal),
    MokieMessage(text="我一直在收集这个啦。", image=MokieImage.normal),
    MokieMessage(text="送我送我送我送我送我。", image=MokieImage.astonish),
    MokieMessage(text="拿来当宠物感觉也不错吧。", image=MokieImage.normal),
    MokieMessage(text="其实我住所后院养了好几笼。", image=MokieImage.normal),
    MokieMessage(text="请不要把他们再扔回来合成了。", image=MokieImage.normal),
    MokieMessage(text="第一次合出来的时候开心一整天。", image=MokieImage.normal),
    MokieMessage(text="在家里放着一堆呢，感觉像是天堂。", image=MokieImage.normal),
    MokieMessage(text="啊啊啊啊啊啊啊啊啊啊啊啊。（表演）", image=MokieImage.astonish),
    MokieMessage(
        text="你那还有多少？我拿一百个老哥跟你换。", image=MokieImage.astonish
    ),
    MokieMessage(
        text="心情不好的时候就学我来给他们顺顺毛吧。", image=MokieImage.normal
    ),
    MokieMessage(
        text="一看到就有好多话想说，可惜一次说不完呢。", image=MokieImage.normal
    ),
)
"榆木华厨的"

MOKIE_MESSAGES_ZERO = (MokieMessage(text="……", image=MokieImage.wtf),)
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
    def have_strange_in_input(self):
        "输入的有奇怪的小哥么"

        for i in self.inputs:
            if i.level.lid == 0 and i.aid != 89:
                return True
        return False

    @property
    def result_is_strange(self):
        return self.result_level == 0 and not self.is_shit

    @property
    def is_strange(self):
        return self.have_strange_in_input or self.result_is_strange

    @property
    def ymh_message(self) -> MokieMessage:
        if self.is_strange:
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


class MergeMeta(BaseModel):
    status: str
    is_strange: bool
    cost_chip: int
    own_chip: int


class YMHMessage(BaseModel):
    text: str
    image: str


class MergeData(BaseModel):
    """
    传递给前端的数据
    """

    inputs: tuple[InfoView, InfoView, InfoView]
    output: Catch
    meta: MergeMeta
    ymh_message: YMHMessage
    name: str

    @staticmethod
    def from_merge_result(data: MergeResult) -> "MergeData":
        return MergeData(
            inputs=(
                InfoView.from_award_info(data.inputs[0]),
                InfoView.from_award_info(data.inputs[1]),
                InfoView.from_award_info(data.inputs[2]),
            ),
            output=Catch(
                info=InfoView.from_award_info(data.output.info),
                count=data.output.count,
                is_new=data.output.is_new,
            ),
            meta=MergeMeta(
                status=data.successed.value,
                is_strange=data.is_strange,
                cost_chip=data.cost_money,
                own_chip=data.remain_money,
            ),
            ymh_message=YMHMessage(
                text=data.ymh_message.text,
                image=data.ymh_message.image.value,
            ),
            name=data.user.name,
        )
