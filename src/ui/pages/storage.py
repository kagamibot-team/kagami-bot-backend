from nonebot_plugin_alconna import UniMessage

from src.ui.base.tools import image_to_bytes
from src.ui.components.list_view import render_document
from src.ui.views.list_view import UserStorageView
from utils.threading import make_async


def render_progress_image(data: UserStorageView):
    return render_document(data.prog_document)


async def render_progress_message(data: UserStorageView):
    return UniMessage.image(
        raw=await make_async(image_to_bytes)(
            await make_async(render_progress_image)(data)
        )
    )
