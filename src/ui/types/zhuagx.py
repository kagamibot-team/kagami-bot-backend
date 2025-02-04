from packaging.version import Version
from pydantic import BaseModel


class UpdateContent(BaseModel):
    content: str
    tags: list[str] = []


class VersionData(BaseModel):
    version: str
    time: str = ""
    updates: list[UpdateContent] = []


class UpdateData(BaseModel):
    current_page: int = 1
    max_page: int = 1
    show_pager: bool
    versions: list[VersionData]


updates: list[VersionData]


def get_latest_version() -> VersionData:
    return get_latest_versions(1)[0]


def get_latest_versions(count: int = 3, shift: int = 0) -> list[VersionData]:
    return updates[shift:][:count]


updates = [
    VersionData(
        version="0.2.0",
        updates=[
            UpdateContent(content="将数据使用数据库储存", tags=["内核"]),
            UpdateContent(content="修复间隔为 0 时报错的问题", tags=["修复"]),
        ],
    ),
    VersionData(
        version="0.2.1",
        updates=[
            UpdateContent(
                content="修复了一些界面文字没有中心对齐的问题", tags=["修复"]
            ),
            UpdateContent(content="修复了抓小哥时没有字体颜色的问题", tags=["修复"]),
        ],
    ),
    VersionData(
        version="0.3.0",
        updates=[
            UpdateContent(content="正式添加皮肤系统", tags=["功能"]),
            UpdateContent(content="限制了管理员指令只能在一些群执行", tags=["内核"]),
            UpdateContent(
                content="修复了新玩家的周期被设置为 3600 的问题", tags=["修复"]
            ),
            UpdateContent(content="重新架构了关于图片生成的代码", tags=["内核"]),
        ],
    ),
    VersionData(
        version="0.4.0",
        updates=[
            UpdateContent(content="添加了商店系统", tags=["功能"]),
        ],
    ),
    VersionData(
        version="0.4.1",
        updates=[
            UpdateContent(content="将版本更新信息倒序而非正序显示", tags=["修复"]),
            UpdateContent(content="调整了库存的显示顺序", tags=["特性"]),
            UpdateContent(content="新抓到小哥能够获得奖励了", tags=["特性"]),
            UpdateContent(content="来・了（数据恢复）"),
        ],
    ),
    VersionData(
        version="0.4.2",
        updates=[
            UpdateContent(
                content="热更新：修复了新用户有关的各种小问题", tags=["修复"]
            ),
        ],
    ),
    VersionData(
        version="0.4.3",
        updates=[
            UpdateContent(content="修复了无法应用多个皮肤的问题", tags=["修复"]),
            UpdateContent(
                content="调整了图片编码器以加快图片的生成速度", tags=["内核"]
            ),
        ],
    ),
    VersionData(
        version="0.4.4",
        updates=[
            UpdateContent(content="调整了抓小哥进度中等级显示的顺序", tags=["特性"]),
            UpdateContent(content="修复了可以靠刷屏多次抓小哥的 BUG", tags=["修复"]),
            UpdateContent(
                content="还有一点，等你抽到了百变小哥就知道了～", tags=["特性"]
            ),
        ],
    ),
    VersionData(
        version="0.4.5",
        updates=[
            UpdateContent(content="修复了抓小哥时没有显示新小哥的问题", tags=["修复"]),
            UpdateContent(
                content="修复了抓小哥展示页面中描述意外断行的问题", tags=["修复"]
            ),
            UpdateContent(
                content="删去了一些判断使得文字的渲染速度能够加快", tags=["内核"]
            ),
        ],
    ),
    VersionData(
        version="0.5.0",
        updates=[
            UpdateContent(
                content="尝试修复了抓小哥时出现的数据库冲突问题", tags=["修复"]
            ),
            UpdateContent(content="更新了一个跟给小哥有关的特性", tags=["特性"]),
        ],
    ),
    VersionData(
        version="0.5.1",
        updates=[
            UpdateContent(content="修复了金钱数量不会增加的问题", tags=["修复"]),
            UpdateContent(content="修复了没有回复人的问题", tags=["修复"]),
        ],
    ),
    VersionData(
        version="0.5.2",
        updates=[
            UpdateContent(content="修复了切换皮肤没有响应的问题"),
            UpdateContent(content="大幅度优化了抓小哥的速度"),
        ],
    ),
    VersionData(
        version="0.5.3",
        updates=[
            UpdateContent(content="修复了和给小哥有关的一个特性"),
            UpdateContent(content="修复了抓小哥界面中皮肤没有正常展示的 Bug"),
            UpdateContent(content="优化了部分指令"),
        ],
    ),
    VersionData(
        version="0.5.4",
        updates=[
            UpdateContent(content="修复了一处数字显示的问题"),
            UpdateContent(content="修复了有些地方金钱没有正常改变的问题"),
        ],
    ),
    VersionData(
        version="0.5.5",
        updates=[
            UpdateContent(content="修复了一些和皮肤有关的问题"),
            UpdateContent(content="给"),
        ],
    ),
    VersionData(
        version="0.5.6",
        updates=[
            UpdateContent(content="修复了mysp不显示单位的问题"),
            UpdateContent(content="删除了对给的回应"),
            UpdateContent(content="添加了喜报"),
            UpdateContent(content="添加了复读镜，现在你可以操作小镜去抓 wum 了"),
        ],
    ),
    VersionData(
        version="0.5.7",
        updates=[
            UpdateContent(content="修复了切换皮肤命令"),
            UpdateContent(content="修复了喜报指令"),
        ],
    ),
    VersionData(
        version="0.5.8",
        updates=[
            UpdateContent(content="现在呼叫小镜，可以加 Emoji 表情和 QQ 表情了"),
            UpdateContent(content="新增了皮肤收集进度指令，看看你收集了多少皮肤"),
            UpdateContent(
                content="AlphaQX: 调整了「复读镜」指令，现在的回应会更加人性化了"
            ),
            UpdateContent(content="MrChenBeta: 新增小镜jrrp指令，快来测测你的人品吧"),
        ],
    ),
    VersionData(
        version="0.5.9",
        updates=[
            UpdateContent(content="优化了小镜商店页面"),
            UpdateContent(content="AlphaQX: 修复复读镜"),
            UpdateContent(content="耶"),
        ],
    ),
    VersionData(
        version="0.5.10",
        updates=[
            UpdateContent(content="耶（已修复）"),
            UpdateContent(content="修复了小镜商店有关的问题"),
            UpdateContent(content="修正了「小镜！！！」时的提示词"),
        ],
    ),
    VersionData(
        version="0.5.11",
        updates=[
            UpdateContent(content="修复了小镜商店中买皮肤不会扣钱的问题"),
            UpdateContent(content="榆木华: 更改了喜报的格式"),
            UpdateContent(content="榆木华: 抓小哥进度添加标题、小哥数量"),
            UpdateContent(content="榆木华: 微调抓进度界面，新增进度百分比计算与显示"),
        ],
    ),
    VersionData(
        version="0.5.12",
        updates=[
            UpdateContent(content="修复小镜商店的 Bug"),
            UpdateContent(content="从本次更新之后，喜报的信息能够持久化保存了"),
            UpdateContent(content="榆木华: 库存界面添加标题"),
            UpdateContent(content="榆木华: 给抓小哥界面加了标题"),
        ],
    ),
    VersionData(
        version="0.5.13",
        updates=[
            UpdateContent(content="在多个地方显示群昵称而不是 QQ 名称"),
            UpdateContent(
                content="修复了一些文字显示的问题，现在支持显示 Emoji 表情了"
            ),
            UpdateContent(content="记得「签到」"),
            UpdateContent(
                content="榆木华：在抓进度界面增加了筛选等级功能，例如 zhuajd -l 5 就可以筛选查看五级的小哥进度"
            ),
            UpdateContent(content="榆木华：修复了小票二维码错位的问题"),
        ],
    ),
    VersionData(
        version="0.5.13.1",
        updates=[
            UpdateContent(
                content="试图修正了 zhuajd 过程中可能出现的 max() arg 为空的问题"
            ),
        ],
    ),
    VersionData(
        version="0.5.14",
        updates=[
            UpdateContent(content="榆木华：调整了全部小哥界面和抓小哥界面的排版等"),
            UpdateContent(content="榆木华：优化签到和jrrp指令，优化帮助信息"),
            UpdateContent(content="榆木华：商店价格加阴影，以防难以辨认"),
        ],
    ),
    VersionData(
        version="0.5.15",
        updates=[
            UpdateContent(content="修复小镜 bot 会无故扣钱的问题"),
            UpdateContent(content="榆木华：在今日人品消息中增加今日小哥"),
            UpdateContent(content="榆木华：在皮肤进度界面添加标题"),
        ],
    ),
    VersionData(
        version="0.5.16",
        updates=[
            UpdateContent(
                content="榆木华：将帮助信息和更新信息改为图片生成，优化了界面"
            ),
        ],
    ),
    VersionData(
        version="0.6.0",
        updates=[
            UpdateContent(content="上线合成系统。"),
        ],
    ),
    VersionData(
        version="0.6.1",
        updates=[
            UpdateContent(content="修正合成系统并回档。"),
        ],
    ),
    VersionData(
        version="0.6.2",
        updates=[
            UpdateContent(content="晚安……"),
            UpdateContent(content="榆木华：调整了合成的相关算法"),
            UpdateContent(content="榆木华：为合成添加了界面！"),
            UpdateContent(content="榆木华：修复了库存为 0 时仍然显示在库存中的问题"),
        ],
    ),
    VersionData(
        version="0.6.3",
        updates=[
            UpdateContent(content="“晚安”指令改为“小镜晚安”，添加了对半个小时的支持"),
            UpdateContent(content="Dleshers沣：喜报中增加了新抓小哥的提示"),
        ],
    ),
    VersionData(
        version="0.6.4",
        updates=[
            UpdateContent(content="是"),
            UpdateContent(content="榆木华：更改了一些消息的文本"),
        ],
    ),
    VersionData(
        version="0.7.0",
        updates=[
            UpdateContent(content="调整了随机数生成器"),
            UpdateContent(content="榆木华：调整了商店的界面"),
            UpdateContent(content="榆木华：降低了合成的难度"),
        ],
    ),
    VersionData(
        version="0.7.1",
        updates=[
            UpdateContent(content="修复了一些指令无法正常使用的问题"),
            UpdateContent(content="修复了新玩家无法正常创建帐号的问题"),
        ],
    ),
    VersionData(
        version="0.7.2",
        updates=[
            UpdateContent(content="owo"),
            UpdateContent(content="修复了一些界面中可能出现的字体缺失问题"),
            UpdateContent(
                content="这次很多更新是在底层进行的，所以还有可能出现一些 bug……"
            ),
            UpdateContent(
                content="距离公测已经不远了，在不久之后，会清空内测阶段的存档，感谢大家一直以来的支持，没有大家，抓小哥不会走到今天！"
            ),
        ],
    ),
    VersionData(
        version="0.8.0",
        updates=[
            UpdateContent(content="引入成就系统（测试中）"),
            UpdateContent(content="修复了重构以后和之前版本不同的一些表现"),
        ],
    ),
    VersionData(
        version="0.8.1",
        updates=[
            UpdateContent(content="修复了一个界面问题"),
        ],
    ),
    VersionData(
        version="0.8.2",
        updates=[
            UpdateContent(content="修复了一个界面问题"),
            UpdateContent(content="修复「欧皇附体」成就判定错误"),
            UpdateContent(content="调整了合成小哥的随机数生成机制"),
            UpdateContent(content="下线了复读镜指令"),
        ],
    ),
    VersionData(
        version="0.8.4",
        updates=[
            UpdateContent(content="榆木华：把今日人品合入签到，并暂时取消显示今日小哥"),
            UpdateContent(content="榆木华：优化合成算法"),
        ],
    ),
    VersionData(
        version="0.8.5",
        updates=[
            UpdateContent(content="修复了输入单撇号会导致报错的问题"),
            UpdateContent(content="叫小镜的时候不会响应粽子表情"),
        ],
    ),
    VersionData(
        version="0.8.6",
        updates=[
            UpdateContent(content="是小哥现在也会给钱了"),
            UpdateContent(content="调整了一些发送消息的时机"),
            UpdateContent(
                content="移除了开头的跳舞，准备试验现在能不能让 bot 更加稳定"
            ),
        ],
    ),
    VersionData(
        version="0.9.0",
        updates=[
            UpdateContent(content="优化了合成的界面"),
            UpdateContent(content="调整了一些消息的文字"),
            UpdateContent(content="为 kz 指令添加了大写的匹配"),
            UpdateContent(content="去除了一个特性"),
            UpdateContent(content="调大了小镜商店的字号"),
        ],
    ),
    VersionData(
        version="0.9.1",
        updates=[
            UpdateContent(content="优化了合成的界面"),
            UpdateContent(content="调整了一些消息的文字"),
            UpdateContent(content="为 kz 指令添加了大写的匹配"),
            UpdateContent(content="去除了一个特性"),
            UpdateContent(content="调大了小镜商店的字号"),
        ],
    ),
    VersionData(
        version="0.10.0",
        updates=[
            UpdateContent(
                content="架构了一个新的底层机制，在界面完成后，将会与大家见面，请大家期待"
            ),
            UpdateContent(content="去除了一个特性"),
            UpdateContent(content="修复了一处字体问题"),
        ],
    ),
    VersionData(
        version="0.10.1",
        updates=[
            UpdateContent(content="修复了小镜不回应某些人的问题"),
        ],
    ),
    VersionData(
        version="0.10.2",
        updates=[
            UpdateContent(content="谁出货了？给他丢粑粑小哥吧！"),
            UpdateContent(
                content="更改了小镜晚安的逻辑，晚安需谨慎哦！真的！！！一定要注意！！！！"
            ),
            UpdateContent(content="榆木华：更新了研究员华的对话"),
        ],
    ),
    VersionData(
        version="0.10.3",
        updates=[
            UpdateContent(content="小帕：调整了百变小哥的合成"),
            UpdateContent(content="玛对：调整成就的显示方式，使其更不让人误解"),
            UpdateContent(content="坏枪：调整了丢粑粑的相关判定"),
        ],
    ),
    VersionData(
        version="1.0.0",
        updates=[
            UpdateContent(content="猎场功能上线", tags=["功能"]),
            UpdateContent(
                content="实现了新的界面渲染方式，这个方案现在进入了测试阶段",
                tags=["内核"],
            ),
        ],
    ),
    VersionData(
        version="1.0.1",
        updates=[
            UpdateContent(content="修复了已知的问题（微信语）", tags=["修复"]),
        ],
    ),
    VersionData(
        version="1.0.2",
        updates=[
            UpdateContent(
                content="修复了不显示用户名的问题，此时将替换为显示 QQ 号",
                tags=["特性"],
            ),
            UpdateContent(content="调整了一些界面", tags=["特性"]),
        ],
    ),
    VersionData(
        version="1.0.3",
        updates=[
            UpdateContent(content="修复了一些用户只能显示 QQ 号的问题", tags=["修复"]),
            UpdateContent(content="在一些界面显示了 QQ 头像", tags=["特性"]),
            UpdateContent(content="调整了一些指令", tags=["特性"]),
        ],
    ),
    VersionData(
        version="1.0.5",
        updates=[
            UpdateContent(
                content="修复了一些指令会意外在闲聊群触发的问题", tags=["修复"]
            ),
            UpdateContent(content="调整了一些错误信息的回复", tags=["特性"]),
            UpdateContent(content="修改了和百变小哥有关的游戏逻辑", tags=["修复"]),
            UpdateContent(content="展示条目的时候同时显示库存和累计", tags=["特性"]),
        ],
    ),
    VersionData(
        version="1.1.0",
        updates=[
            UpdateContent(content="新增了一个 NPC", tags=["特性"]),
        ],
    ),
    VersionData(
        version="1.1.1",
        updates=[
            UpdateContent(content="修复了合成时可能出现的外键问题", tags=["修复"]),
            UpdateContent(content="更改了更新界面", tags=["界面"]),
        ],
    ),
    VersionData(
        version="1.1.2",
        updates=[
            UpdateContent(
                content="迁移了大量代码到前端渲染，有些界面可能会有一些位移",
                tags=["内核", "界面"],
            ),
            UpdateContent(content="修复了小镜晚安的连胜日期问题", tags=["修复"]),
            UpdateContent(content="榆木华：调整了小镜 Bot 的帮助信息", tags=["功能"]),
            UpdateContent(content="修复了重复汇报版本更新的问题", tags=["修复"]),
        ],
    ),
    VersionData(
        version="1.1.3",
        updates=[
            UpdateContent(content="修复了若干已知的问题", tags=["修复"]),
            UpdateContent(
                content="为小镜 Bot 的自动更新等功能做了简单的基础", tags=["内核"]
            ),
        ],
    ),
    VersionData(
        version="1.1.4",
        updates=[
            UpdateContent(
                content="这几天一直在修复渲染器的问题", tags=["修复", "内核"]
            ),
            UpdateContent(
                content="坏枪：修复了一些页面潜在的渲染问题", tags=["修复", "界面"]
            ),
            UpdateContent(content="修复了库存等界面的比例错误", tags=["修复", "界面"]),
        ],
    ),
    VersionData(
        version="1.1.5",
        updates=[
            UpdateContent(content="修复了小镜晚安指令线程不安全的问题", tags=["修复"]),
        ],
    ),
    VersionData(
        version="1.2.0",
        updates=[
            UpdateContent(
                content="榆木华：上线合成档案查询功能，请输入“抓小哥帮助 合成档案”查看详细内容",
                tags=["功能"],
            ),
            UpdateContent(
                content="榆木华：合成界面添加剩余库存量的显示", tags=["特性", "界面"]
            ),
            UpdateContent(
                content="坏枪：修复了一些页面潜在的渲染问题", tags=["修复", "界面"]
            ),
        ],
    ),
    VersionData(
        version="1.2.1",
        updates=[UpdateContent(content="热更新，修复了若干 Bug", tags=["修复"])],
    ),
    VersionData(
        version="1.2.2",
        updates=[
            UpdateContent(content="修正合成档案功能的错误可用范围", tags=["修复"]),
            UpdateContent(
                content="榆木华：修正合成百变小哥获得皮肤的异常表现", tags=["修复"]
            ),
            UpdateContent(
                content="榆木华：修正抓进度中消耗完的小哥不显示库存为0的问题",
                tags=["修复", "界面"],
            ),
            UpdateContent(
                content="榆木华：增加四五星获得时的发光，优化小哥边框，修复售罄的表现",
                tags=["特性", "修复", "界面"],
            ),
        ],
    ),
    VersionData(
        version="1.2.3",
        updates=[
            UpdateContent(content="更改部分界面样式", tags=["界面"]),
            UpdateContent(content="榆木华：调整金暴性的表现", tags=["特性"]),
            UpdateContent(
                content="榆木华：删除所有猎场信息错误的配方（合成档案的使用不受影响）",
                tags=["修复"],
            ),
        ],
    ),
    VersionData(
        version="1.2.4",
        updates=[
            UpdateContent(
                content="榆木华：将抓进度中的进度百分比改为“哥度”。",
                tags=["特性", "界面"],
            ),
            UpdateContent(
                content="榆木华：新增“我有多少哥度（mygd）”指令。", tags=["功能"]
            ),
            UpdateContent(content="榆木华：将mysp显示的值修复为整数。", tags=["修复"]),
        ],
    ),
    VersionData(version="1.2.5", updates=[UpdateContent(content="常规更新")]),
    VersionData(version="1.2.6", updates=[UpdateContent(content="更改了一些对话")]),
    VersionData(
        version="1.2.7",
        updates=[
            UpdateContent(
                content="更换字体，以解决“忽”、“耀”等字显示错误的问题。", tags=["界面"]
            ),
            UpdateContent(
                content="榆木华：抓进度与库存中，装备了皮肤的小哥现在将显示皮肤。",
                tags=["界面"],
            ),
            UpdateContent(
                content="榆木华：修正了抓小哥界面 1 号猎场不显示的问题。", tags=["界面"]
            ),
        ],
    ),
    VersionData(
        version="1.2.8",
        updates=[
            UpdateContent(
                content="修复了和抓小哥冷却时间判断有关的问题", tags=["修复"]
            ),
        ],
    ),
    VersionData(
        version="1.2.9",
        updates=[
            UpdateContent(content="修复了展示小哥的一处逻辑漏洞", tags=["修复"]),
            UpdateContent(content="调整了后端的资源管理内核", tags=["核心"]),
        ],
    ),
    VersionData(
        version="1.2.10",
        updates=[
            UpdateContent(content="修复了一些内核 Bug", tags=["修复"]),
        ],
    ),
    VersionData(
        version="1.2.11",
        updates=[UpdateContent(content="修改了和皮肤有关的底层逻辑", tags=["核心"])],
    ),
    VersionData(
        version="1.2.12",
        updates=[
            UpdateContent(content="修复了皮肤的描述没有正确显示的问题", tags=["修复"])
        ],
    ),
    VersionData(
        version="1.2.13",
        updates=[
            UpdateContent(
                content="修复了在替换协议端内核时出现的无法展示的问题", tags=["修复"]
            ),
            UpdateContent(
                content="修复了即将推出的新功能的内核中存在的问题", tags=["修复"]
            ),
        ],
    ),
]


updates = sorted(updates, reverse=True, key=lambda i: Version(i.version))
