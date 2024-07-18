from nonebot_plugin_alconna import UniMessage
from interfaces.nonebot.components.list_view import render_document
from src.common.decorators.threading import make_async
from src.common.draw.tools import imageToBytes
from src.views.list_view import UserStorageView


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
