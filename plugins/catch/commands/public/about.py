"""
显示更新信息
"""

from nonebot_plugin_alconna import UniMessage
from ...events.context import PublicContext
from ...events import root
from ...events.decorator import listenPublic, matchRegex


updateHistory: dict[str, list[str]] = {
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
}


updateHistoryDev: dict[str, list[str]] = {
    "0.4.5": [
        "调整了删除小哥的指令，会连带删除与它相关的其他数据",
    ],
    "0.5.0": [
        "重构了整个任务系统，从现在开始，将要慢慢迁移指令到新的任务系统",
        "使用 Alconna 分析指令",
        "添加了在控制台执行指令的功能",
    ],
}


help: list[str] = [
    "抓小哥帮助(zhuahelp)：显示这条帮助信息",
    "抓小哥更新(zhuagx)：显示抓小哥的更新信息",
    "关于抓小哥(zhuaabout)：显示抓小哥的介绍",
    "抓小哥(zhua)：进行一次抓",
    "狂抓小哥(kz)：一次抓完所有可用次数",
    "库存(kc)：展示个人仓库中的存量",
    "抓小哥进度(zhuajd)：展示目前收集的进度",
    "切换皮肤 小哥名字：切换一个小哥的皮肤",
    "小镜的shop(xjshop)：进入小镜的商店",
    "我有多少薯片(mysp)：告诉你你有多少薯片",
]


helpAdmin: list[str] = [
    "::help",
    "::zhuagx",
    "::所有小哥",
    "::所有等级",
    "::设置周期 秒数",
    "::设置小哥 名称/图片/等级/描述 小哥的名字",
    "::设置等级 名称/权重/颜色/金钱/优先 等级的名字 值",
    "::删除小哥 小哥的名字",
    "::创建小哥 名字 等级",
    "::创建等级 名字",
    "/give qqid 小哥的名字 (数量)",
    "/clear (qqid (小哥的名字))",
    "::创建皮肤 小哥名字 皮肤名字",
    "::更改皮肤 名字/图片/描述/价格 皮肤名字",
    "::获得皮肤 皮肤名字",
    "::剥夺皮肤 皮肤名字",
    "::展示 小哥名字 (皮肤名字)",
    "::重置抓小哥上限（注意这个是对所有人生效的）",
    "::给钱 qqid 钱",
    "::添加小哥/等级/皮肤别称 原名 别称",
    "::删除小哥/等级/皮肤别称 别称",
]


def constructUpdateMessage(updates: dict[str, list[str]], count: int = 5) -> UniMessage:
    """
    构造更新信息
    """

    text = "===== 抓小哥更新 =====\n"

    for key in sorted(updates.keys(), reverse=True):
        if count == 0:
            break

        count -= 1
        text += f"{key}:\n"
        for item in updates[key]:
            text += f"- {item}\n"

    return UniMessage().text(text)


def constructHelpMessage(helps: list[str]) -> UniMessage:
    """
    构造帮助信息
    """

    text = "===== 抓小哥帮助 =====\n"

    for item in helps:
        text += f"- {item}\n"
    
    return UniMessage().text(text)


@listenPublic(root)
@matchRegex("^(抓小哥|zhua) ?(更新|gx|upd|update)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructUpdateMessage(updateHistory))


@listenPublic(root)
@matchRegex("^:: ?(抓小哥|zhua) ?(更新|gx|upd|update)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructUpdateMessage(updateHistoryDev))


@listenPublic(root)
@matchRegex("^(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructHelpMessage(help))


@listenPublic(root)
@matchRegex("^:: ?(抓小哥|zhua) ?(帮助|help)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(constructHelpMessage(helpAdmin))


@listenPublic(root)
@matchRegex("^(关于 ?抓小哥|zhua ?about)$")
async def _(ctx: PublicContext, *_):
    await ctx.send(UniMessage().text("以后再写，详见 https://github.com/Passthem-desu/passthem-bot"))