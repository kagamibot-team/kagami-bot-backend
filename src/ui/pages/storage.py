from nonebot_plugin_alconna import UniMessage

from src.ui.base.tools import imageToBytes
from src.ui.components.list_view import render_document
from src.ui.views.list_view import UserStorageView
from utils.threading import make_async


def render_progress_image(data: UserStorageView):
    return render_document(data.prog_document)


def render_storage_image(data: UserStorageView):
    return render_document(data.storage_document)


async def render_progress_message(data: UserStorageView):
    return UniMessage.image(
        raw=await make_async(imageToBytes)(
            await make_async(render_progress_image)(data)
        )
    )


async def render_storage_message(data: UserStorageView):
    return UniMessage.image(
        raw=await make_async(imageToBytes)(await make_async(render_storage_image)(data))
    )
