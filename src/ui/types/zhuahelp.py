from pydantic import BaseModel


class HelpPair(BaseModel):
    key: str
    value: str


class HelpParam(BaseModel):
    note: str
    content: list[HelpPair]


class HelpData(BaseModel):
    command: str
    description: str
    required_parameters: HelpParam | None
    optional_parameters: HelpParam | None
    related_commands: HelpParam | None


command_dict: dict[str, str] = {
    "抓小哥": "抓小哥",
    "zhua": "抓小哥",
    "狂抓": "狂抓",
    "kz": "狂抓",
    "展示": "展示",
    "库存": "库存",
    "kc": "库存",
    "抓小哥进度": "抓小哥进度",
    "zhuajd": "抓小哥进度",
    "我的成就": "我的成就",
    "mycj": "我的成就",
    "合成": "合成",
    "hc": "合成",
    "合成档案": "合成档案",
    "hcda": "合成档案",
    "小鹅猎场": "小鹅猎场",
    "xelc": "小鹅猎场",
    "购买猎场": "购买猎场",
    "gmlc": "购买猎场",
    "切换猎场": "切换猎场",
    "qhlc": "切换猎场",
    "小镜商店": "小镜商店",
    "xjshop": "小镜商店",
    "我有多少薯片": "我有多少薯片",
    "mysp": "我有多少薯片",
    "我有多少哥度": "我有多少哥度",
    "mygd": "我有多少哥度",
    "皮肤进度": "皮肤进度",
    "pfjd": "皮肤进度",
    "切换皮肤": "切换皮肤",
    "小镜签到": "小镜签到",
    "xjqd": "小镜签到",
    "小镜晚安": "小镜晚安",
    "丢粑粑": "丢粑粑",
    "是": "是",
    "金暴性": "金暴性",
    "kbs": "金暴性",
    "抓小哥帮助": "抓小哥帮助",
    "zhuahelp": "抓小哥帮助",
    "抓小哥更新": "抓小哥更新",
    "zhuagx": "抓小哥更新",
    "关于小镜bot": "关于小镜bot",
    "kagamiabout": "关于小镜bot",
    "pfsd": "皮肤商店",
    "皮肤商店": "皮肤商店",
}

command_content: dict[str, HelpData] = {
    "抓小哥": HelpData(
        command="抓小哥（zhua）",
        description="操纵bot抓数次小哥。",
        required_parameters=None,
        optional_parameters=HelpParam(
            note="",
            content=[
                HelpPair(
                    key=r"{次数N}",
                    value="有足够次数的情况下抓N次小哥，否则抓完目前积攒的所有次数。",
                ),
            ],
        ),
        related_commands=HelpParam(
            note="",
            content=[
                HelpPair(key="狂抓（kz）", value="一次抓完所有可用次数。"),
            ],
        ),
    ),
    "狂抓": HelpData(
        command="狂抓（kz）",
        description="一次抓完目前积攒的所有次数。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "展示": HelpData(
        command="展示",
        description="展示指定小哥或皮肤的详细信息。",
        required_parameters=HelpParam(
            note="",
            content=[
                HelpPair(key=r"{小哥名X}", value="指明需要展示信息的小哥X。"),
            ],
        ),
        optional_parameters=HelpParam(
            note="（可叠加）",
            content=[
                HelpPair(
                    key="-d",
                    value="以抓取条目的形式展示该小哥。每个小哥左下白数字表示目前的存量，左上的黑数字表示获得过的总数。",
                ),
                HelpPair(key=r"-s {皮肤名X}", value="指明需要展示信息的皮肤X。"),
            ],
        ),
        related_commands=None,
    ),
    "库存": HelpData(
        command="库存（kc）",
        description="展示个人目前可用于消耗的小哥存量。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "抓小哥进度": HelpData(
        command="抓小哥进度(zhuajd)",
        description="展示个人小哥的收集进度，并在不限定等级时按一定的算法计算收集进度的百分比。每个小哥左下白数字表示目前的存量，左上的黑数字表示获得过的总数。",
        required_parameters=None,
        optional_parameters=HelpParam(
            note="（可叠加）",
            content=[
                HelpPair(key=r"lv {等级名X}", value="仅展示等级为X的小哥进度。"),
                HelpPair(key=r"lc {猎场号N}", value="仅展示在猎场N可抓的小哥进度。"),
            ],
        ),
        related_commands=None,
    ),
    "我的成就": HelpData(
        command="我的成就（mycj）",
        description="展示成就列表，暂仅用文字展示并标出已达成的成就。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "合成": HelpData(
        command="合成（hc）",
        description="使用合成功能，将三个任意小哥进行合成。",
        required_parameters=HelpParam(
            note="",
            content=[
                HelpPair(
                    key=r"{小哥名X1} {小哥名X2} {小哥名X3}",
                    value="将X1、X2、X3三个小哥送入合成机器。",
                ),
            ],
        ),
        optional_parameters=None,
        related_commands=None,
    ),
    "合成档案": HelpData(
        command="合成档案（hcda）",
        description="消耗薯片，从全服合成历史中查询指定小哥的三条合成配方。配方按“自身库存满足配方需求的程度”从高到低排序，即三个小哥都有的配方会排在只拥有其中两个的前面。程度相同的则越新越前。\n零星到五星的查询价格为：1、2、4、8、16与32薯片。",
        required_parameters=HelpParam(
            note="",
            content=[
                HelpPair(
                    key=r"{小哥名X}",
                    value="查询合成出小哥X的配方。",
                ),
            ],
        ),
        optional_parameters=None,
        related_commands=None,
    ),
    "小鹅猎场": HelpData(
        command="小鹅猎场（xelc）",
        description="展示小鹅猎场界面。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=HelpParam(
            note="",
            content=[
                HelpPair(key="购买猎场（gmlc）", value="花费货币购买指定猎场。"),
                HelpPair(key="切换猎场（qhlc）", value="按顺序切换抓小哥所在猎场。"),
            ],
        ),
    ),
    "购买猎场": HelpData(
        command="购买猎场（gmlc）",
        description="花费货币，解锁指定猎场的使用权限。",
        required_parameters=HelpParam(
            note="",
            content=[
                HelpPair(key=r"{猎场号N}", value="指定购买N号猎场。"),
            ],
        ),
        optional_parameters=None,
        related_commands=None,
    ),
    "切换猎场": HelpData(
        command="切换猎场（qhlc）",
        description="按顺序在已解锁猎场中切换抓小哥所在猎场。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "小镜商店": HelpData(
        command="小镜商店（xjshop）",
        description="展示小镜商店里的商品与其信息。",
        required_parameters=None,
        optional_parameters=HelpParam(
            note="",
            content=[
                HelpPair(key=r"购买 {商品名X}", value="购买名为X的商品。"),
            ],
        ),
        related_commands=None,
    ),
    "我有多少薯片": HelpData(
        command="我有多少薯片（mysp）",
        description="展示个人薯片量，暂仅用文字说明。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "我有多少哥度": HelpData(
        command="我有多少哥度（mygd）",
        description="展示总哥度数值，暂仅用文字说明。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "皮肤进度": HelpData(
        command="皮肤进度（pfjd）",
        description="展示个人小哥的皮肤收集进度，界面暂定。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "切换皮肤": HelpData(
        command="切换皮肤",
        description="装备或卸下购得或其他途径获得的皮肤。",
        required_parameters=HelpParam(
            note="(选其一)",
            content=[
                HelpPair(key=r"{小哥名X}", value="将小哥X切换为所拥有的下一个皮肤。"),
                HelpPair(key=r"{皮肤名X}", value="将拥有皮肤X的小哥切换至该皮肤。"),
            ],
        ),
        optional_parameters=None,
        related_commands=None,
    ),
    "小镜签到": HelpData(
        command="小镜签到（xjqd）",
        description="每天可以签一次到，奖励玩家1~100中随机量的薯片。同时会统计连续签到天数，连续天数越多奖励大量薯片概率越高。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "小镜晚安": HelpData(
        command="小镜晚安",
        description="使自己进入相对小镜bot的休眠模式，仅响应不含游戏性的部分指令，直至设定的起床时间为止。\n起床时间可设定为四点到十点的任意一个整点或半点，指令可使用时间则为21:00起至设定的起床时间为止。23:00前使用本指令，会奖励玩家50~100中随机量的薯片。",
        required_parameters=None,
        optional_parameters=HelpParam(
            note="",
            content=[
                HelpPair(
                    key=r"{时间点X}",
                    value="自然语言写出的时间点（仅限整点或半点），如“明早八点”、“五点半”等。（留空默认为“八点”）",
                ),
            ],
        ),
        related_commands=None,
    ),
    "丢粑粑": HelpData(
        command="丢粑粑",
        description="@一个群友（不能是自己），并同时说出“丢”或“吃”的近义词与“粑粑”的近义词，即可耗费库存内的一个粑粑小哥试着丢向对方！成功的话会进入对方的库存，但也有概率失败，粑粑直接消失。示例：“@小镜bot 赤石吧！！！”",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "是": HelpData(
        command="是",
        description="若有抓的次数，则消耗一次直接固定抓取是小哥；若没有，则将下一抓的猎物预定为是小哥，小镜回复“收到”；已预定则无其他效果，小镜回复“是”。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "金暴性": HelpData(
        command="金暴性",
        description="若获得过代表“金”、“暴”和“性”的全部三种小哥，则在说出含有“金”、“暴”、“性”或者“sex”中任一关键字词的发言时，直接触发小镜提示，获取并切换三小哥的[三要素]皮肤。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "抓小哥帮助": HelpData(
        command="抓小哥帮助（zhuahelp）",
        description="展示指令列表与大致说明信息。",
        required_parameters=None,
        optional_parameters=HelpParam(
            note="",
            content=[
                HelpPair(key=r"{指令名X}", value="展示指令X的详细帮助。"),
            ],
        ),
        related_commands=None,
    ),
    "抓小哥更新": HelpData(
        command="抓小哥更新（zhuagx）",
        description="展示抓小哥的更新信息，可翻阅自撰写更新信息以来的所有内容。",
        required_parameters=None,
        optional_parameters=HelpParam(
            note="",
            content=[
                HelpPair(
                    key=r"{页码N}", value="展示更新信息的第N页。（留空默认为“1”）"
                ),
            ],
        ),
        related_commands=None,
    ),
    "关于小镜bot": HelpData(
        command="关于小镜bot（kagamiabout）",
        description="展示在QQ运作的小镜bot的部分信息。",
        required_parameters=None,
        optional_parameters=None,
        related_commands=None,
    ),
    "皮肤商店": HelpData(
        command="皮肤商店（pfsd）",
        description="展示皮肤商店里的商品与其信息。",
        optional_parameters=HelpParam(
            note="",
            content=[
                HelpPair(key=r"购买 {商品名X}", value="购买名为X的商品。"),
            ],
        ),
        required_parameters=None,
        related_commands=None,
    )
}
