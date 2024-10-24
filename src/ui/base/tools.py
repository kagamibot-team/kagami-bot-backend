import cv2
import numpy as np
import PIL
import PIL.Image


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    assert len(hex_color) == 7 or len(hex_color) == 4

    if len(hex_color) == 4:
        hex_color = "#" + hex_color[1] * 2 + hex_color[2] * 2 + hex_color[3] * 2

    return (int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb  # pylint: disable=consider-using-f-string


def mix_color(
    rgb1: tuple[int, int, int], rgb2: tuple[int, int, int], ratio: float = 0.5
):
    return (
        int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio),
        int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio),
        int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio),
    )


def image_to_bytes(img: PIL.Image.Image, suffix: str = ".png") -> bytes:
    arr = np.array(img)

    if arr.ndim == 2:
        arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    if arr.shape[2] == 2:
        lightness, alpha = cv2.split(arr)
        arr = np.zeros((lightness.shape[0], lightness.shape[1], 4), dtype=np.uint8)

        # Assign channels
        arr[:, :, 0] = lightness  # Red channel
        arr[:, :, 1] = lightness  # Green channel
        arr[:, :, 2] = lightness  # Blue channel
        arr[:, :, 3] = alpha  # Alpha channel
    if arr.shape[2] == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    else:
        arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGBA)

    _, im = cv2.imencode(suffix, arr)

    return im.tobytes()


__all__ = ["hex_to_rgb", "rgb_to_hex", "mix_color", "image_to_bytes"]
