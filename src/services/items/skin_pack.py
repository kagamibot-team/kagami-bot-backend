from nonebot_plugin_alconna import UniMessage
from src.base.command_events import MessageContext
from src.core.unit_of_work import UnitOfWork
from src.services.items.base import BaseItem, UseItemArgs


class ItemSkinPack(BaseItem[int]):
    name: str = "皮肤盲盒"
    description: str = "打开来，你可以获得一个随机的皮肤"
    group: str = "消耗品"

    async def can_be_used(self, uow: UnitOfWork, uid: int, args: UseItemArgs) -> bool:
        return True

    async def use(self, uow: UnitOfWork, uid: int, args: UseItemArgs):
        args.require_count_range(1, 1)
        args.require_target(False)
        remain = await self.use_item_in_db(uow, uid, 1)
        return remain

    async def send_use_message(self, ctx: MessageContext, data: int):
        await ctx.reply(
            UniMessage.text(
                f"你使用了一个皮肤盲盒，但是，现在还没有写逻辑，所以什么也没发生。你还有 {data} 个皮肤盲盒"
            )
        )
