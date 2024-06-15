"""
该文件需要转移到 utils 中
"""

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    assert len(hex_color) == 7 or len(hex_color) == 4

    if len(hex_color) == 4:
        hex_color = "#" + hex_color[1] * 2 + hex_color[2] * 2 + hex_color[3] * 2

    return (int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % rgb


def mix_color(
    rgb1: tuple[int, int, int], rgb2: tuple[int, int, int], ratio: float = 0.5
):
    return (
        int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio),
        int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio),
        int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio),
    )


__all__ = ['hex_to_rgb', 'rgb_to_hex', 'mix_color']
