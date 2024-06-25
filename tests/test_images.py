import unittest

import PIL
import PIL.Image

from src.common.draw.images import horizontalPile, pileImages, verticalPile


class TestImages(unittest.IsolatedAsyncioTestCase):
    async def test_piles(self):
        images = [
            PIL.Image.new("RGB", (10, 10)),
            PIL.Image.new("RGB", (5, 20)),
            PIL.Image.new("RGBA", (20, 20)),
        ]

        hori = await horizontalPile(images, 11, "center")

        self.assertEqual(hori.width, 57)
        self.assertEqual(hori.height, 20)

        verti = await verticalPile(images, 3, "left")

        self.assertEqual(verti.width, 20)
        self.assertEqual(verti.height, 56)
