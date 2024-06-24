from packaging.version import Version


class Messages:
    catch_top = """剩余抓小哥的次数：{0}/{1}\n下次次数恢复还需要{2}\n你刚刚一共抓了{3}只小哥，并得到了{4}\n现在，你一共有{5}"""
    mysp = "你有{}"
    skin_set = "已经将皮肤设置为 {} 了"
    skin_set_default = "已经将 {} 的皮肤设置为默认了"
    skin_set_2 = "已将 {0} 的皮肤更换为 {1} 了"

    award_create_success = "成功创建名字叫 {} 的小哥。"
    award_delete_success = "成功删除名字叫 {} 的小哥。"

    default_reply = "在"


class Error:
    award_not_found = "没有叫 {} 的小哥。"
    award_exists = "名字叫 {} 的小哥已存在。"

    level_not_found = "等级 {} 不存在。"

    award_not_encountered_yet = "你还没有遇到过叫做 {} 的小哥"
    catch_not_available = "小哥还没长成，请再等{}吧！"
    log_no_gei = "这个世界没有给小哥"

    not_found = "你说的 {} 不存在"
    not_own = "你还没有 {}"

    invalid_catch_count = "你想让我抓 {} 个小哥，你让我怎么抓嘛！"


class Warning:
    log_multi_skin = "用户 {} 有多个应用了的皮肤，将其清空"
    log_use_skin_not_exists = "用户 {} 应用了不存在的皮肤"


class Loading:
    zhuajd = "正在回想你遇到过的小哥……"
    kc = "正在清点仓库里的小哥数量……"
    all_xg = "正在生成图片……"
    zhua = "抓小哥机正在运作中……"
    kz = "抓小哥机正在运作中……"
    pfjd = "正在回想你见过的皮肤……"


class Display:
    award_display = "{}【{}】"
    award_display_with_skin = "{}[{}]【{}】"
    award_unknown_name = "???"
    skin_using = "使用中"


class Unit:
    second = "秒"
    minute = "分钟"
    hour = "小时"

    money = "薯片"


class Develop:
    database_not_found = "数据库文件不存在"


class About:
    about = "关于抓小哥：\n以后再写，详见 https://github.com/Passthem-desu/passthem-bot"
    help_header = "===== 抓小哥帮助 ====="
    update_header = "===== 抓小哥更新 ====="
    help: list[str] = [
        "抓小哥帮助(zhuahelp)：显示这条帮助信息",
        "抓小哥更新(zhuagx)：显示抓小哥的更新信息",
        "关于抓小哥(zhuaabout)：显示抓小哥的介绍",
        "抓小哥(zhua)：进行一次抓",
        "狂抓(kz)：一次抓完所有可用次数",
        "喜报(xb)：最近 24 小时内群里有谁抓到了四/五星",
        "库存(kc)：展示个人仓库中的存量",
        "抓小哥进度(zhuajd)：展示目前收集的进度",
        "切换皮肤 小哥名字：切换一个小哥的皮肤",
        "小镜的shop(xjshop)：进入小镜的商店",
        "我有多少薯片(mysp)：告诉你你有多少薯片",
        "复读镜：叫小镜读一段话",
        "小镜jrrp：今日人品……",
        "皮肤收集进度(pfjd)：展示目前收集小哥皮肤的进度",
        "签到：就是签个到而已",
    ]
    help_admin: list[str] = [
        "::help",
        "::zhuagx",
        "::所有小哥",
        "::所有等级",
        "::设置周期 秒数",
        "::设置小哥 小哥的名字 [名称 新名字] [描述 新描述] [图片 带一张图] [等级 等级的名字]",
        "::设置等级 名称/权重/颜色/金钱/优先 等级的名字 值",
        "::删除小哥 小哥的名字",
        "::创建小哥 名字 等级",
        "::创建等级 名字",
        "/give qqid 小哥的名字 (数量)",
        "/clear (qqid (小哥的名字))",
        "::创建皮肤 小哥名字 皮肤名字",
        "::更改皮肤 名字/图片/描述/价格 皮肤名字（等待转移，这个指令估计也有 Bug）",
        "::获得皮肤 皮肤名字",
        "::剥夺皮肤 皮肤名字",
        "::展示 小哥名字 (皮肤名字)",
        "::重置抓小哥上限（注意这个是对所有人生效的）",
        "::给钱 qqid 钱",
        "::添加小哥/等级/皮肤别称 原名 别称",
        "::删除小哥/等级/皮肤别称 别称",
        "::发送存档",
    ]
    update: dict[str, list[str]] = {
        "0.2.0": [
            "将数据使用数据库储存",
            "修复间隔为 0 时报错的问题",
        ],
        "0.2.1": [
            "修复了一些界面文字没有中心对齐的问题",
            "修复了抓小哥时没有字体颜色的问题",
        ],
        "0.3.0": [
            "正式添加皮肤系统",
            "限制了管理员指令只能在一些群执行",
            "修复了新玩家的周期被设置为 3600 的问题",
            "重新架构了关于图片生成的代码",
        ],
        "0.4.0": [
            "添加了商店系统",
        ],
        "0.4.1": [
            "将版本更新信息倒序而非正序显示",
            "调整了库存的显示顺序",
            "新抓到小哥能够获得奖励了",
            "来・了（数据恢复）",
        ],
        "0.4.2": [
            "热更新：修复了新用户有关的各种小问题",
        ],
        "0.4.3": [
            "修复了无法应用多个皮肤的问题",
            "调整了图片编码器以加快图片的生成速度",
        ],
        "0.4.4": [
            "调整了抓小哥进度中等级显示的顺序",
            "修复了可以靠刷屏多次抓小哥的 BUG",
            "还有一点，等你抽到了百变小哥就知道了～",
        ],
        "0.4.5": [
            "修复了抓小哥时没有显示新小哥的问题",
            "修复了抓小哥展示页面中描述意外断行的问题",
            "删去了一些判断使得文字的渲染速度能够加快",
        ],
        "0.5.0": [
            "尝试修复了抓小哥时出现的数据库冲突问题",
            "更新了一个跟给小哥有关的特性",
        ],
        "0.5.1": [
            "修复了金钱数量不会增加的问题",
            "修复了没有回复人的问题",
        ],
        "0.5.2": [
            "修复了切换皮肤没有响应的问题",
            "大幅度优化了抓小哥的速度",
        ],
        "0.5.3": [
            "修复了和给小哥有关的一个特性",
            "修复了抓小哥界面中皮肤没有正常展示的 Bug",
            "优化了部分指令",
        ],
        "0.5.4": [
            "修复了一处数字显示的问题",
            "修复了有些地方金钱没有正常改变的问题",
        ],
        "0.5.5": [
            "修复了一些和皮肤有关的问题",
            "给",
        ],
        "0.5.6": [
            "修复了mysp不显示单位的问题",
            "删除了对给的回应",
            "添加了喜报",
            "添加了复读镜，现在你可以操作小镜去抓 wum 了",
        ],
        "0.5.7": [
            "修复了切换皮肤命令",
            "修复了喜报指令",
        ],
        "0.5.8": [
            "现在呼叫小镜，可以加 Emoji 表情和 QQ 表情了",
            "新增了皮肤收集进度指令，看看你收集了多少皮肤",
            "AlphaQX: 调整了「复读镜」指令，现在的回应会更加人性化了",
            "MrChenBeta: 新增小镜jrrp指令，快来测测你的人品吧",
        ],
        "0.5.9": [
            "优化了小镜商店页面",
            "AlphaQX: 修复复读镜",
            "耶",
        ],
        "0.5.10": [
            "耶（已修复）",
            "修复了小镜商店有关的问题",
            "修正了「小镜！！！」时的提示词",
        ],
        "0.5.11": [
            "修复了小镜商店中买皮肤不会扣钱的问题",
            "榆木华: 更改了喜报的格式",
            "榆木华: 抓小哥进度添加标题、小哥数量",
            "榆木华: 微调抓进度界面，新增进度百分比计算与显示",
        ],
        "0.5.12": [
            "修复小镜商店的 Bug",
            "从本次更新之后，喜报的信息能够持久化保存了",
            "榆木华: 库存界面添加标题",
            "榆木华: 给抓小哥界面加了标题",
        ],
        "0.5.13": [
            "在多个地方显示群昵称而不是 QQ 名称",
            "修复了一些文字显示的问题，现在支持显示 Emoji 表情了",
            "记得「签到」",
            "榆木华：在抓进度界面增加了筛选等级功能，例如 zhuajd -l 5 就可以筛选查看五级的小哥进度",
            "榆木华：修复了小票二维码错位的问题",
        ],
        "0.5.13.1": [
            "试图修正了 zhuajd 过程中可能出现的 max() arg 为空的问题",
        ]
    }
    update_dev: dict[str, list[str]] = {
        "0.4.5": [
            "调整了删除小哥的指令，会连带删除与它相关的其他数据",
        ],
        "0.5.0": [
            "重构了整个任务系统，从现在开始，将要慢慢迁移指令到新的任务系统",
            "使用 Alconna 分析指令",
            "添加了在控制台执行指令的功能",
        ],
        "0.5.1": [
            "添加了 EventManager.throw 方法，用于不阻塞地抛出事件",
            "现在的 Asyncio 锁已经应用到所有人了，应该能减少一些锁冲突",
        ],
        "0.5.2": [
            "因为优化充分，相信已经不会出现数据库锁超时问题了",
            "将更改小哥和更改皮肤指令迁移到了新指令系统中",
            "修复了 SQLite 不会自动判断外键的问题",
            "Bot 初始化的时候使用多线程预渲染，以保证生产环境能在一分钟内启动",
        ],
        "0.5.3": [
            "让抓小哥的逻辑更加清晰。流程上添加了 PicksEvent 和 PrePickMessageEvent，为以后开发成就系统和其他触发条件做准备",
            "转移了 kc zhuajd ::所有小哥 三个指令到新指令系统，并优化了它们的数据库操作",
        ],
        "0.5.4": [
            "添加了单元测试模块，可以在脱离生产环境的情况下方便地检测逻辑实现的问题。只需要直接运行 run_tests.py 即可展开单元测试",
            "添加了语言模块，将所有文字单独归类到了一个文件中",
        ],
        "0.5.5": [
            "添加了对皮肤的 CRUD 操作的单元测试",
        ],
        "0.5.6": [
            "调整了 Picks 等类的接口，添加了对当前群聊的 ID 记录，以对接喜报系统",
        ],
        "0.5.7": [
            "在后台添加了 ::backup-full 方法，以方便获得数据备份文件",
        ],
        "0.5.8": [
            "在 .gitignore 中屏蔽了 Nonebot Console 的截图文件，以防止误传",
            "添加了 MY_NAME 配置项，用于在自营 bot 中调整称呼 bot 的方式",
            "添加了 now_datetime 方法，用于获取当前时间。请在以后获取事件的时候，都使用这个方法",
            "修正了单元测试的基类文件名，保证该文件不会在未来被单独涵盖在内",
            "对 UniContext 的 reply 和 send 方法支持传入字符串，以后调用的时候可以省一点事",
            "添加了代码看门狗，在开发环境下，在一些文件夹创建 / 删除 / 修改 `.py` 文件的时候，会自动重载，再也不用重启 bot 了（我也讨厌频繁重启 bot）",
            "调整了::所有皮肤指令，现在会返回一张图片",
        ],
        "0.5.9": [
            "重构了 Context 上下文类，添加了对 PublicContext 的单元测试的支持",
            "移动 fast_import 到 src.imports 以缩减 import 的层级",
            "在 Github 的 README 页面中补充了 AQX 和 MCB 的参与",
            "添加了对 qrcode 库的依赖。如果你之前部署过，请额外安装这个库",
            "添加了单元测试的自动导入，你只需要在 tests/ 文件夹中创建一个以 .py 结尾的文件，然后运行 run_tests.py 即可展开单元测试",
        ],
        "0.5.10": [
            "添加了 User 表的几个字段，为签到系统开发做准备",
            "添加了小派上的自动部署的脚本，每天晚上的额定时间，将会自动从 master 分支拉取更新并重新部署",
        ],
        "0.5.11": [
            "XQC 难绷 histroy",
            "榆木华：XQC 难绷「XQC 难绷 histroy」",
            "迁移了所有等级、更改周期两个指令到新系统",
            "重构解耦了 UniContext 相关的定义，不再与 Nonebot 标准协议完全贴合，并为单元测试提供了 Mock 环境所需要的类。如果需要调用 OnebotV11 API，请使用 call_api 方法",
            "更新信息现在已经可以以正确的顺序排序了",
        ],
        "0.5.12": [
            "将大部分 dataclass 迁移到 Pydantic",
            "添加了 OnebotContext 合并转发消息和贴表情的接口",
            "榆木华：修复 verticalPile 多一行 paddingY 的 bug",
            "榆木华：优化 drawLimitedBoxOfTextClassic 函数",
        ],
        "0.5.13": [
            "載陔賸珨跺朸贈源楊ㄛ褫眕汜傖掩з呯腔苤貊芞砉",
            "将文字渲染模块全局替换为了 imagetext-py 库的封装",
            "添加了 ::发送存档 指令，可以在不用网线连接机器的情况下下载存档",
            "添加了 Bot 连接事件的接口，并添加了设置在线状态的 API 枚举类",
            "分离了部分 API",
            "现在会输出日志文件了，可以方便调试，位置在 data/log.log",
            "修复了转换时间戳函数中因为缺少时区信息而报错的问题",
            "添加了抓小哥的小哥组的相关字段，并在未来会逐渐启用",
            "榆木华：添加了抓进度中，零权重小哥只有获得后才会显示的特性",
            "榆木华：添加了和皮肤有关的函数",
            "榆木华：添加了获得隐藏皮肤时的回应",
            "榆木华：全部小哥界面也有筛选等级的指令参数了",
        ],
    }


class La:
    dev = Develop()
    err = Error()
    disp = Display()
    loading = Loading()
    unit = Unit()
    msg = Messages()
    warn = Warning()
    about = About()


la = La()


def get_latest_version() -> str:
    return sorted(la.about.update.keys(), reverse=True, key=Version)[0]


def get_latest_versions(count: int=3) -> list[str]:
    return sorted(la.about.update.keys(), reverse=True, key=Version)[:count]
