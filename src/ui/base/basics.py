import PIL
import PIL.Image


def paste_image(raw: PIL.Image.Image, src: PIL.Image.Image, x: int, y: int):
    raw.alpha_composite(src, (x, y))
