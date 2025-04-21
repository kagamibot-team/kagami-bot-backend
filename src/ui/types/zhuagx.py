from packaging.version import Version
from pydantic import BaseModel

from src.common.times import is_april_fool


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
    VersionData(
        version="1.2.14",
        updates=[
            UpdateContent(
                content="修复了在替换协议端内核时出现的无法 kbs 的问题", tags=["修复"]
            ),
            UpdateContent(content="为未来的更新做好准备工作", tags=["特性"]),
        ],
    ),
    VersionData(
        version="1.3",
        updates=[UpdateContent(content="皮肤商店更新", tags=["特性"])],
    ),
    VersionData(
        version="1.3.1",
        updates=[
            UpdateContent(content="修复了一些小哥无法被查询的问题", tags=["修复"]),
        ],
    ),
    VersionData(
        version="1.3.2",
        updates=[
            UpdateContent(content="修复了使用皮肤盲盒时可能存在的数据回退", tags=["修复"]),
        ],
    )
]


april_fool = VersionData(
    version="2.0.0",
    updates=[
        UpdateContent(
            content="小镜 BOT 迁移至了基于华为鲲鹏计算芯片、运行 OpenEuler 操作系统的华为云上运行。",
            tags=["运维"],
        ),
        UpdateContent(
            content="小镜 BOT 从项目管理、产品研发、DevOps 到运维，已全线接入 DeepSeek-R1 全量满血版大模型，赋能小镜 BOT 领导新质生产力，创造时代新价值。",
            tags=["运维", "AI"],
        ),
        UpdateContent(
            content="抓小哥团队购进了摩尔线程 MTT X300 显卡集群，加速小镜 BOT 图片渲染。",
            tags=["运维", "界面"],
        ),
        UpdateContent(
            content="小镜 BOT 后端使用了 Rust 重构，不同模块实现了解耦。如果你感兴趣，可以下载小镜 BOT 的源码，使用 k8s 部署 Docker 集群。",
            tags=["内核"],
        ),
        UpdateContent(
            content="因版权方要求，删除了W.G.皇家科学院相关设定，并订正了剧情涉及小哥的文案描述。",
            tags=["剧情"],
        ),
        UpdateContent(
            content="稍微调整了NPC 吃鱼 的精力限制——在此问题修复前，贝塔会因为遛狗工作过于艰巨而在工作岗位上睡大觉，并说梦话。",
            tags=["剧情"],
        ),
        UpdateContent(
            content="稍微调整了NPC吃鱼 与 NPC 拾 的互动限制；在此问题修复前，这两位NPC有概率在啤酒馆地点互动时触发一些预料之外的事件链。",
            tags=["剧情"],
        ),
        UpdateContent(
            content="几乎每天都来上班打卡的华，今天怎么会无故缺勤呢？请使用hc功能来看看华走了之后的合成部吧！另外，他去干什么了呢？",
            tags=["剧情"],
        ),
        UpdateContent(
            content="稍微调整了“其他”种类小哥的某些属性……不过这好像导致档案部出现了一些奇怪的事情，请使用查询功能来看看档案部现在变成了什么样子吧！另外，为什么会这样呢？",
            tags=["剧情"],
        ),
        UpdateContent(
            content="L和鸽出去玩了，结果猎场却？？？？？？？？？？？？？？？？？？请使用 xelc功能来看看猎场的一日皇帝是谁吧！另外，他哪来的？",
            tags=["剧情"],
        ),
        UpdateContent(
            content="救救我！这个站点有人要杀我",
            tags=["救命"],
        ),
        UpdateContent(
            content="因未知原因，小哥猎手们会使用小哥进行类昆特牌对战，此问题仍待修复。",
            tags=["剧情"],
        ),
        UpdateContent(
            content="因为移除了“回转企鹅罐”的内轮梗，愤怒的壳泡将魔爪（饮料）伸向了……请使用 pfsd 功能来看看服装店发生了哪些变化吧！另外，壳泡哪里来的这么大脾气？",
            tags=["剧情"],
        ),
        UpdateContent(
            content="小镜 BOT 会记下你在闲聊群的消息，并根据你对小镜的态度决定各商店商品价格，但是不会用于 LLM 模型训练。",
            tags=["功能", "AI"],
        ),
        UpdateContent(
            content="NPC 贝塔现在会在群内选择活跃的小哥猎手填写个人资料问卷，并且贝塔表示绝对不会将这些资料投入在“物质本质探索”等研究课题上。",
            tags=["功能", "AI"],
        ),
        UpdateContent(
            content="小镜商店即将迎来大装修，现在你可以看到小镜的上半身立绘了。",
            tags=["功能"],
        ),
        UpdateContent(
            content="投掷粑粑功能加入了对战模式，可对指定玩家或 NPC 发送“吔屎啦你”来开启对战。",
            tags=["功能"],
        ),
        UpdateContent(
            content="小镜商店推出「补签卡」。如果你忘记签到了，可以在小镜商店购买！",
            tags=["功能"],
        ),
        UpdateContent(
            content="""小镜商店推出「抢劫」功能。可发送「xjshop 抢劫」对小镜进行抢劫并大概率免费获得商品内容！
目前可公开的：
抢劫成功有概率获得：1-99个粑粑小哥，1-3个小华，9薯片，卡槽上线，小镜等。
抢劫失败则可能遭受惩罚：获得1-99个粑粑小哥/被小镜禁言一天并被小镜每小时投喂一次粑粑小哥/3小时内无法进行kz/被小镜做成小哥/转生来到小哥世界。""",
            tags=["功能"],
        ),
        UpdateContent(
            content="修复了开包界面中，「塩立绘」会挡住部分描述的问题。",
            tags=["修复", "界面"],
        ),
        UpdateContent(
            content="修复了在某些极端情况下，小哥描述过长导致的NPC下半身露出问题。",
            tags=["修复", "界面"],
        ),
        UpdateContent(
            content="修复了在某些情况下，英俊小哥发色异常的问题。",
            tags=["修复"],
        ),
        UpdateContent(
            content="修复了小坏枪在被小哥猎手抓到时描述出现刷屏和精神污染的问题。",
            tags=["修复"],
        ),
        UpdateContent(
            content="修复了鹦鹉小哥的颜色显示问题。",
            tags=["修复"],
        ),
        UpdateContent(
            content="修复了百变小哥[小抽子]的图片显示异常问题——修复前，此问题导致 百变小哥[小抽子]显示为L。",
            tags=["修复"],
        ),
        UpdateContent(
            content="巩固了小卷毛鱼的海洋霸主地位。",
            tags=["修复"],
        ),
        UpdateContent(
            content="修复了小卷毛鱼的海洋霸主地位，现在它被重新安置进了番茄罐里。",
            tags=["修复"],
        ),
        UpdateContent(
            content="修复了因玩家名字过长而无法显示抓取内容的异常问题。",
            tags=["修复"],
        ),
        UpdateContent(
            content='为深入贯彻落实国家绿色低碳发展战略全局部署，我司技术团队针对小镜BOT人工智能系统开展了系统性技术优化与迭代升级。以李忠牵头的研究小组通过算法重构与算力调度机制革新，成功解决了历史版本中存在的非必要算力资源挤占问题（涉及与DeepSeek、ChatGPT等平台的冗余竞争性运算），该项技术攻关标志着人工智能领域节能减排工作取得突破性进展。经国际标准化组织(ISO)环境效益计量体系验证，本次升级改造累计节约标准煤0.11111111qr克当量。pastebin.com/ySENxdr1这一成果充分彰显我司作为行业领军企业，在践行生态文明建设、推动数字经济绿色发展方面的责任担当。未来我们将继续秉持"算力向善"理念，积极探索人工智能与碳中和战略深度融合的创新路径，为构建清洁美丽世界贡献科技力量。',
            tags=["修复", "AI"],
        ),
        UpdateContent(
            content="修复了某些情况下，中山大学宿舍的电费账单会寄送至小哥研究所的问题。现在此电费账单将由小镜BOT向各位小哥猎手们征收。",
            tags=["修复"],
        ),
        UpdateContent(
            content="蛋糕不再是谎言，双皮奶也是。",
            tags=["修复"],
        ),
        UpdateContent(
            content="修复了部分小哥猎手库存内粑粑小哥过多的问题——在此问题修复前，L会偷偷往部分小哥猎手的库存里搬粑粑小哥。",
            tags=["修复"],
        ),
        UpdateContent(
            content="现在黑市功能已经实装！您可以通过指令 xchs 来查询我们精心设计的黑市界面，以及新的NPC：槽！（和蒜）",
            tags=["更新"],
        ),
        UpdateContent(
            content="""新增超级迷你猎场功能，您可以通过指令 xelc 来查询新的超级迷你猎场。现在已经开放的超级迷你猎场：超级至尊无敌小猎场；售价 20 薯片，其中包含：小哥，小哥，小哥，小哥。
打金服猎场；售价 999 薯片，其中包含：至尊VIP小哥，骷髅小哥，怨♂灵小哥
W.G.皇家科学院海外飞地猎场；售价 114514 小哥，其中包含：燃！！！！！！！！！小哥。
苞米地猎场；暂不开放。
救赎猎场；暂不开放。""",
            tags=["更新"],
        ),
        UpdateContent(
            content="""新增电子海主题猎场功能。您可以通过指令xelc来查询新的猎场。内有大量和古早迷因小哥以及新的猎场npc等待你探寻！
包含新的猎场 NPC ：幽灵纱。
包含可能出现的新小哥：千年虫小哥，XP小哥，2000小哥，摩哥密码，PS小哥，AE小哥、Reaper小哥、Vegas Pro小哥、Aviutl小哥、Blender小哥。""",
            tags=["更新"],
        ),
        UpdateContent(
            content="移除了 Xiaogebrine。",
            tags=["更新"],
        ),
        UpdateContent(
            content="Caroline 已被删除。",
            tags=["更新"],
        ),
        UpdateContent(
            content="""新增地点：小哥农园！通过指令 xgny 与小镜BOT进行互动，与其他NPC们一起探索NPC 沣建设的新时代农业体系庄园吧！
小哥农园现支持的功能：
xgny 送一朵花给沣：可以给沣送一朵花。""",
            tags=["更新"],
        ),
        UpdateContent(
            content="新增功能：小哥宇宙切换！现在可以切换到其他小哥宇宙进行新小哥的抓捕，输入 xgyz 以查看当前可切换的宇宙。当前宇宙：狗。可切换宇宙：2077，深海，美食，锤子，合同，烟花，鱼，停电。",
            tags=["更新"],
        ),
    ],
)


if is_april_fool():
    updates = updates + [april_fool]


updates = sorted(updates, reverse=True, key=lambda i: Version(i.version))
