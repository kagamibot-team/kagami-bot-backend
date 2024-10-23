from enum import Enum
from pathlib import Path

from src.base.res.middleware.filter import WithPrefixFilter, WithSuffixFilter
from src.base.res.middleware.image import ResizeMiddleware
from src.base.res.strategy import (
    CombinedStorageStrategy,
    FileStorageStrategy,
    FilteredStorageStrategy,
    JustFallBackStorageStrategy,
    ShadowStorageStrategy,
    StaticStorageStrategy,
)


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
                FileStorageStrategy(Path("./data/skins")), WithSuffixFilter("sid_")
            ),
            JustFallBackStorageStrategy(Path("./res/default.png")),
        ]
    )
    "小哥和皮肤图片的资源"

    xiaoge_low = ShadowStorageStrategy(
        xiaoge,
        FileStorageStrategy(Path("./data/temp/low")),
        ResizeMiddleware(175, 140),
    )
    "低分辨率的小哥和皮肤图片资源"
