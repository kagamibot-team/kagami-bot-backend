import os
import pathlib
from typing import Literal
import uuid
import PIL
import PIL.Image
import PIL.ImageTransform
import PIL.ImageFilter

from src.common.decorators.threading import make_async


@make_async
def newImage(size: tuple[int, int] = (500, 500), color: str = "white"):
    img = PIL.Image.new("RGBA", size, color)
    return img


@make_async
def loadImage(fp: str):
    image = PIL.Image.open(fp)
    return image.convert("RGBA")


@make_async
def imagePaste(raw: PIL.Image.Image, src: PIL.Image.Image, x: int, y: int):
    raw.paste(src, (x, y), src.convert("RGBA"))


@make_async
def resize(img: PIL.Image.Image, width: int, height: int):
    return img.resize((width, height))


async def blurred(fp: str, radius: int):
    filename = uuid.uuid5(uuid.NAMESPACE_URL, fp).hex
    fpo = os.path.join(pathlib.Path("./data/temp/"), f"blurred_{radius}_{filename}.png")

    if os.path.exists(fpo):
        return fpo

    img = await loadImage(fp)
    img = img.filter(PIL.ImageFilter.BoxBlur(radius))
    img.save(fpo)
    return fpo


async def horizontalPile(
    images: list[PIL.Image.Image],
    paddingX: int,
    align: Literal["top", "bottom", "center"],
    background: str = "#00000000",
    marginTop: int = 0,
    marginLeft: int = 0,
    marginRight: int = 0,
    marginBottom: int = 0,
) -> PIL.Image.Image:
    maxHeight = max([i.height for i in images] + [1])
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

        await imagePaste(base, image, leftPointer + marginLeft, top + marginTop)
        leftPointer += image.width + paddingX

    return base


async def verticalPile(
    images: list[PIL.Image.Image],
    paddingY: int,
    align: Literal["left", "center", "right"],
    background: str = "#00000000",
    marginTop: int = 0,
    marginLeft: int = 0,
    marginRight: int = 0,
    marginBottom: int = 0,
) -> PIL.Image.Image:
    maxWidth = max([i.width for i in images] + [1])
    height = sum([i.height for i in images]) + paddingY * (len(images) - 1)

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

        await imagePaste(base, image, left + marginLeft, topPointer + marginTop)
        topPointer += image.height + paddingY

    return base


async def pileImages(
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
    "imagePaste",
    "horizontalPile",
    "verticalPile",
    "pileImages",
    "resize",
    "blurred",
]
