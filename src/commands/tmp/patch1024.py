# 于 2024/10/24 创建的，仅用于临时修补的文件
# 将在未来版本中删除


from pathlib import Path

from src.base.command_events import MessageContext
from src.common.command_deco import listen_message, match_literal, require_admin
from src.core.unit_of_work import get_unit_of_work


@listen_message()
@require_admin()
@match_literal("::patch1024")
async def patch1024(ctx: MessageContext):
    # 这次修补是将 ./data/awards/ 和 ./data/skins/ 内的不用的文件清除。

    async with get_unit_of_work() as uow:
        images = [Path(v) for _, v in (await uow.awards.get_all_images()).items()]
        award_dir = Path("./data/awards/")

        for img in award_dir.iterdir():
            if img not in images:
                img.unlink()

        images = [Path(v) for _, v in (await uow.skins.get_all_images()).items()]
        skin_dir = Path("./data/skins/")

        for img in skin_dir.iterdir():
            if img not in images:
                img.unlink()

    await ctx.send("修补完成。")
