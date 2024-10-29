from pathlib import Path

from src.base.res.middleware.filter import WithPrefixFilter
from src.base.res.middleware.image import BlurMiddleware, ResizeMiddleware, ToRGBAMiddleware
from src.base.res.strategy import (
    CombinedStorageStrategy,
    FileStorageStrategy,
    FilteredStorageStrategy,
    JustFallBackStorageStrategy,
    ShadowStorageStrategy,
    StaticStorageStrategy,
    TempdirStorageStrategy,
)
from src.base.res.urls import resource_url_registerator


class KagamiResourceManagers:
    res = CombinedStorageStrategy(
        [
            StaticStorageStrategy(Path("./res")),
            JustFallBackStorageStrategy(),
        ]
    )
    "静态资源"

    xiaoge = CombinedStorageStrategy(
        [
            FilteredStorageStrategy(
                FileStorageStrategy(Path("./data/awards")), WithPrefixFilter("aid_")
            ),
            FilteredStorageStrategy(
                FileStorageStrategy(Path("./data/skins")), WithPrefixFilter("sid_")
            ),
            StaticStorageStrategy(Path("./res")),
            JustFallBackStorageStrategy(Path("./res/default.png")),
        ]
    )
    "小哥和皮肤图片的资源"

    xiaoge_low = ShadowStorageStrategy(
        xiaoge,
        FileStorageStrategy(Path("./data/temp/low")),
        [ResizeMiddleware(175, 140), ToRGBAMiddleware()],
    )
    "低分辨率的小哥和皮肤图片资源"

    xiaoge_blurred = ShadowStorageStrategy(
        xiaoge,
        FileStorageStrategy(Path("./data/temp/blurred")),
        [ResizeMiddleware(175, 140), BlurMiddleware(10), ToRGBAMiddleware()],
    )

    tmp = TempdirStorageStrategy()
    "临时文件资源"

    url_manager = resource_url_registerator
    "资源URL管理器"


def blank_placeholder():
    return KagamiResourceManagers.res("blank_placeholder.png")
