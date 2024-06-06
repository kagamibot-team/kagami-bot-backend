import enum
import PIL
import PIL.Image
import PIL.ImageTransform

import numpy as np
import cv2
import cv2.typing

from .typing import Cv2Image, PILImage


def loadImage(fp: str):
    image = PIL.Image.open(fp)
    return image.convert("RGBA")


def addUponPaste(raw: PILImage, src: PILImage, x: int, y: int):
    raw.paste(src, (x, y), src.convert("RGBA"))


def toOpenCVImage(raw: PILImage):
    return cv2.cvtColor(np.array(raw), cv2.COLOR_RGB2BGR)


def fromOpenCVImage(raw: Cv2Image):
    return PIL.Image.fromarray(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))


def fastPaste(raw: Cv2Image, src: Cv2Image, x: int, y: int):
    raw[y: y + src.shape[0], x: x + src.shape[1]] = src


def addUpon(
    raw: PILImage,
    src: PILImage,
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
