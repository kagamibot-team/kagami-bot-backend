import enum
import PIL
import PIL.Image
import PIL.ImageTransform

from .typing import IMAGE


def loadImage(fp: str):
    image = PIL.Image.open(fp)
    return image.convert("RGBA")


def addUponPaste(raw: IMAGE, src: IMAGE, x: int, y: int):
    raw.paste(src, (x, y), src)


def addUpon(
    raw: IMAGE,
    src: IMAGE,
    x: float,
    y: float,
    anchorX: float = 0.5,
    anchorY: float = 0.5,
    scaleX: float = 1,
    scaleY: float = 1,
):
    transform = PIL.ImageTransform.AffineTransform((
        1 / scaleX,
        0,
        (anchorX * src.size[0] - x) / scaleX,
        0,
        1 / scaleY,
        (anchorY * src.size[1] - y) / scaleY,
    ))

    src = src.convert('RGBA')

    _src = src.convert('RGB').transform(
        raw.size, transform.method, transform.data, PIL.Image.Resampling.BILINEAR, 0
    )

    _srcMask = src.split()[3].transform(
        raw.size, transform.method, transform.data, PIL.Image.Resampling.BILINEAR, 0
    )

    raw.paste(_src, (0, 0), _srcMask)
