import enum
from typing import Literal
import PIL
import PIL.Image
import PIL.ImageTransform

import numpy as np
import cv2
import cv2.typing

from src.common.decorators.threading import make_async


@make_async
def newImage(size: tuple[int, int] = (500, 500), color: str = "white"):
    img = PIL.Image.new("RGB", size, color)
    return img


@make_async
def loadImage(fp: str):
    image = PIL.Image.open(fp)
    return image.convert("RGBA")


@make_async
def addUponPaste(raw: PIL.Image.Image, src: PIL.Image.Image, x: int, y: int):
    raw.paste(src, (x, y), src.convert("RGBA"))


@make_async
def toOpenCVImage(raw: PIL.Image.Image):
    return cv2.cvtColor(np.array(raw), cv2.COLOR_RGB2BGR)


@make_async
def fromOpenCVImage(raw: cv2.typing.MatLike):
    return PIL.Image.fromarray(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))


@make_async
def fastPaste(raw: cv2.typing.MatLike, src: cv2.typing.MatLike, x: int, y: int):
    raw[y : y + src.shape[0], x : x + src.shape[1]] = src


@make_async
def addUpon(
    raw: PIL.Image.Image,
    src: PIL.Image.Image,
    x: float,
    y: float,
    anchorX: float = 0.5,
    anchorY: float = 0.5,
    scaleX: float = 1,
    scaleY: float = 1,
):
    transform = PIL.ImageTransform.AffineTransform(
        (
            1 / scaleX,
            0,
            (anchorX * src.size[0] - x) / scaleX,
            0,
            1 / scaleY,
            (anchorY * src.size[1] - y) / scaleY,
        )
    )

    src = src.convert("RGBA")

    _src = src.convert("RGB").transform(
        raw.size, transform.method, transform.data, PIL.Image.Resampling.BILINEAR, 0
    )

    _srcMask = src.split()[3].transform(
        raw.size, transform.method, transform.data, PIL.Image.Resampling.BILINEAR, 0
    )

    raw.paste(_src, (0, 0), _srcMask)


@make_async
def resize(img: PIL.Image.Image, width: int, height: int):
    return img.resize((width, height))


async def horizontalPile(
    images: list[PIL.Image.Image],
    paddingX: int,
    align: Literal["top", "bottom", "center"],
    background: str,
    marginTop: int = 0,
    marginLeft: int = 0,
    marginRight: int = 0,
    marginBottom: int = 0,
) -> PIL.Image.Image:
    maxHeight = max([i.height for i in images])
    width = sum([i.width for i in images]) + paddingX * len(images)

    base = await newImage(
        (width + marginLeft + marginRight, maxHeight + marginTop + marginBottom),
        background,
    )
    leftPointer = 0

    for image in images:
        if align == "top":
            top = 0
        elif align == "bottom":
            top = maxHeight - image.height
        else:
            top = (maxHeight - image.height) // 2

        await addUponPaste(base, image, leftPointer + marginLeft, top + marginTop)
        leftPointer += image.width + paddingX

    return base


async def verticalPile(
    images: list[PIL.Image.Image],
    paddingY: int,
    align: Literal["left", "center", "right"],
    background: str,
    marginTop: int = 0,
    marginLeft: int = 0,
    marginRight: int = 0,
    marginBottom: int = 0,
) -> PIL.Image.Image:
    maxWidth = max([i.width for i in images])
    height = sum([i.height for i in images]) + paddingY * len(images)

    base = await newImage(
        (maxWidth + marginLeft + marginRight, height + marginTop + marginBottom),
        background,
    )
    topPointer = 0

    for image in images:
        if align == "left":
            left = 0
        elif align == "right":
            left = maxWidth - image.width
        else:
            left = (maxWidth - image.width) // 2

        await addUponPaste(base, image, left + marginLeft, topPointer + marginTop)
        topPointer += image.height + paddingY

    return base


async def combineABunchOfImage(
    paddingX: int,
    paddingY: int,
    images: list[PIL.Image.Image],
    rowMaxNumber: int,
    background: str,
    horizontalAlign: Literal["top", "center", "bottom"],
    verticalAlign: Literal["left", "center", "right"],
    marginLeft: int = 0,
    marginRight: int = 0,
    marginTop: int = 0,
    marginBottom: int = 0,
):
    piles: list[PIL.Image.Image] = []

    i = 0

    while images[i : i + rowMaxNumber]:
        piles.append(
            await horizontalPile(
                images[i : i + rowMaxNumber],
                paddingX,
                horizontalAlign,
                background,
                0,
                marginLeft,
                marginRight,
                0,
            )
        )

        i += rowMaxNumber

    return await verticalPile(
        piles, paddingY, verticalAlign, background, marginTop, 0, 0, marginBottom
    )


__all__ = [
    "newImage",
    "loadImage",
    "addUponPaste",
    "toOpenCVImage",
    "fromOpenCVImage",
    "fastPaste",
    "addUpon",
    "horizontalPile",
    "verticalPile",
    "combineABunchOfImage",
    "resize",
]
