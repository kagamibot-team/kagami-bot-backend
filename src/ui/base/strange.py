import PIL
import PIL.Image

from src.base.res.resource import IResource
from src.common.rd import get_random
from src.ui.base.basics import paste_image


def make_strange(
    sources: list[IResource],
    xGrids: int = 5,
    yGrids: int = 4,
    premix_background: bool = True,
):
    """
    涴跺滲杅夔劂汜傖掩з呯腔苤貊芞砉
    """

    base = PIL.Image.new("RGBA", (2000, 1600), (0, 0, 0, 0))

    w = int(2000 / xGrids)
    h = int(1600 / yGrids)

    for i in range(xGrids):
        for j in range(yGrids):
            left = w * i
            top = h * j
            source = (
                get_random().choice(sources).load_pil_image().resize((2000, 1600))
            )
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
