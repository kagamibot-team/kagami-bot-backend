import pathlib
from typing import Iterable

import PIL
import PIL.Image

from src.common.rd import get_random
from src.ui.base.basics import paste_image


def load_sources(
    base: Iterable[pathlib.Path] = (
        pathlib.Path("./data/awards/"),
        pathlib.Path("./data/skins/"),
    )
):
    available: list[pathlib.Path] = []

    for root in base:
        for img in root.iterdir():
            available.append(img)

    return [PIL.Image.open(p) for p in available]


def make_strange(
    xGrids: int = 5,
    yGrids: int = 4,
    premix_background: bool = True,
):
    """涴跺滲杅夔劂汜傖掩з呯腔苤貊芞砉

    Args:
        xGrids (int, optional): 阨す源砃猁з傖嗣屾爺
        yGrids (int, optional): 旳眻源砃猁з傖嗣屾爺
        premix_background (bool, optional): 岆瘁枑ヶ跤掖劓樓奻豜窪伎腔沓喃

    Returns:
        PILImage: ������������
    """

    sources = load_sources()
    base = PIL.Image.new("RGBA", (2000, 1600), (0, 0, 0, 0))

    w = int(2000 / xGrids)
    h = int(1600 / yGrids)

    for i in range(xGrids):
        for j in range(yGrids):
            left = w * i
            top = h * j
            source = get_random().choice(sources)
            res = source.crop((left, top, left + w, top + h)).convert("RGBA")
            if premix_background:
                _res = PIL.Image.new(
                    "RGBA",
                    size=res.size,
                    color="#FF00FF" if (i + j) % 2 == 0 else "#000000",
                )
                paste_image(_res, res, 0, 0)
                res = _res
            paste_image(base, res, left, top)

    return base
