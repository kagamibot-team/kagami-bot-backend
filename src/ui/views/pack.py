"""
猎场 UI 的数据
"""

from enum import Enum
from random import Random

from pydantic import BaseModel

from src.ui.views.catch import InfoView, LevelView
from src.ui.views.user import UserData


class LQRExpressionImage(Enum):
    coming = "我来啦"
    normal = "正常"


class LQRExpression(BaseModel):
    text: str
    face: LQRExpressionImage


EXPRESSIONS = [
    LQRExpression(
        text="咋打咧（咋打猎）？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="1号猪场……是养猪的吗？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="老爷爷，我又来拿手指祸害人间啦！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="谁帮我设一下，我不知道现在的代码改啥样了，",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我想一下。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="哇嘎嘎嘎！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="耶！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="你那随意吧。（那你）",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="你不要看我，我不知道！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="瓦塔西哇erodesu，找夜神月。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="不是，到底是干啥的啊，真的要一百句没关系的话吗！？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="有給……",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="艹！艹！kz！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="啊？你要买猎场，什么猎场。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="什么意思？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="这薯片是给我吃的吗？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="（他们没跟我说还得接待人啊，求回复教程......）",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="耶……",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="干嘛！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="干嘛……",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="为什么我凉气开了30度还这么热啊？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="怎么才第22句，求放过。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我来啦！",
        face=LQRExpressionImage.coming,
    ),
    LQRExpression(
        text="啥时候更的新，我又跟不上了...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="哟西，小鬼子！哟西，小鬼子！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="哈哈！隔壁那个研究员华是不是又私吞了两坨屎！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我说了我不懂啊！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="嗨给~",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="主播救我...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="REVERSE！哇嘎嘎嘎你来看门！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="你的小哥，都是我的啦！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="若敢来犯，必叫你大饱而归！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="这不是站街！这至少是看门吧！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我也不懂啊...听他们说有学分就来了...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="谁说我是人机了...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="XX杀...？不熟，真的不熟...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="虽然不知道里面是干什么的，但是看到那两个四星的绿毛就帮我抓两只吧。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="还要多久才能进入你的...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="这样抗一天枪也好累啊...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="带了枪过来怎么只是看门儿啊？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="kz。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="写起来意外的轻松呢...虽然还是不知道里面是干什么的。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="饿了...上次铁锅炖大鹅剩了一半...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="旁边这几个小哥是干嘛的啊？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="求教程。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我是谁，我在哪，我在做什么。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="清晨时，睁开眼，问自己几何。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我看不懂，你去问隔壁小槽吧。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="啊~要变成化石了啊~~~",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="电吹风，呼呼呼呼呼呼呼呼呼呼呼呼呼呼呼。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="你干嘛哈哈哎哟~~~",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="欧耶~",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="蹲门口蹲的脚酸了...谁来告诉我里面是干啥的啊？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="这么强？！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="这么弱？？？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="有点儿强。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="Hello大家好，欢迎来到小L的小哥游戏时间，今天里面还是看不懂在干嘛。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="@长崎素十 给。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="输入“是”有惊喜哦。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="[好！]",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="不听不听，王八念经~",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="他们说不懂也可以来的，我就来了。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="妈，你打吧。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="有点想在草原上开德克士。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="悄悄肘击一下隔壁的小华，嘘！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="dark♂的要来了。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="温馨提示：粑粑小哥可以搓粑粑球玩哦！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="那咋了？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="今天就这些，就问你要不要吧！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="悄悄告诉你，其他几个npc都打不过我哇嘎嘎嘎！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="谁敢舔？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="你老婆。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="你老公。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="好处说完了，那坏处呢？",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="那一定是你抓小哥不够努力。[图片]",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="人生就俩字儿：kz。",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="呜呜呜。。。小哥。。。你一定要和你教培啊。。。[图片]",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="老板让我加班设计台词，臣妾做不到啊！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我这可以打猎，小华那不可以，因此我一胜，小华零胜，因此我两胜，小华零胜，因此我三胜，小华零胜，因此我完胜。[图片]",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我是不是人呐，我到底是不是人呐！",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="我感觉身在庐中不知庐...",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="/敬礼",
        face=LQRExpressionImage.normal,
    ),
    LQRExpression(
        text="他们说的，我负责站着如喽罗",
        face=LQRExpressionImage.normal,
    ),
]


class LevelCollectProgress(BaseModel):
    level: LevelView
    collected: int
    sum_up: int


class SinglePackView(BaseModel):
    """
    玩家的其中一个猎场的视图
    """

    pack_id: int
    "猎场的 ID"

    award_count: list[LevelCollectProgress]
    "各个等级，玩家收集了多少小哥，以及各有多少个小哥"

    featured_award: InfoView
    "这个猎场最特色的小哥，用于在界面中展示"

    unlocked: bool
    "用户解锁了这个猎场了么"


def get_random_expression(random: Random) -> LQRExpression:
    return random.choice(EXPRESSIONS)


class PackView(BaseModel):
    """
    玩家的猎场的视图
    """

    packs: list[SinglePackView]
    "所有的猎场"

    user: UserData
    "用户的信息"

    selecting: int
    "用户选择的猎场"

    expression: LQRExpression
    "小鹅表情"
