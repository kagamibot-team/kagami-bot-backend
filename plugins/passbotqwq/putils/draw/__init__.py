import base64
import io
from typing import Tuple
import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

from ..threading import make_async

from .typing import PILImage, PillowColorLike, PillowColorLikeWeak


FONT_HARMONYOS_SANS = r'C:\Windows\Fonts\HarmonyOS_Sans_SC_Regular.ttf'
FONT_HARMONYOS_SANS_BLACK = r'C:\Windows\Fonts\HarmonyOS_Sans_SC_Black.ttf'


@make_async
def newImage(size: Tuple[int, int] = (500, 500), color: PillowColorLike = 'white'):
    img = PIL.Image.new('RGB', size, color)
    return img


def imageToBytes(img: PILImage):
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()
