import tempfile
from pathlib import Path
from unittest import TestCase

import PIL
import PIL.Image

from src.base.res.middleware.filter import WithPrefixFilter, WithSuffixFilter
from src.base.res.middleware.image import ResizeMiddleware
from src.base.res.strategy import (
    CombinedStorageStrategy,
    FileStorageStrategy,
    FilteredStorageStrategy,
    JustFallBackStorageStrategy,
    ShadowStorageStrategy,
    StaticStorageStrategy,
)


class TestStrategy(TestCase):
    def test_static(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tdir = Path(tempdir)
            strategy = StaticStorageStrategy(tdir)

            # Test Readonly
            self.assertFalse(strategy.can_put("123"))
            with self.assertRaises(NotImplementedError):
                strategy.put("test1.png", b"")

            # Test Read
            self.assertFalse(strategy.exists("kagami"))
            (tdir / "kagami").write_bytes(b"114514")
            self.assertTrue(strategy.exists("kagami"))
            self.assertEqual(strategy.get("kagami").path, tdir / "kagami")

    def test_fs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tdir = Path(tempdir)
            strategy = FileStorageStrategy(tdir)
            strategy.put("kagami", b"123456")
            self.assertEqual(strategy.get("kagami").path.read_bytes(), b"123456")
            self.assertTrue(strategy.exists("kagami"))
            self.assertFalse(strategy.exists("tsukasa"))
            strategy.put("kagami", b"123456")
            self.assertEqual(strategy.get("kagami").path.read_bytes(), b"123456")

    def test_shadow(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tdir = Path(tempdir)
            (tdir / "main").mkdir()
            strategy = FileStorageStrategy(tdir / "main")
            _shadow = FileStorageStrategy(tdir / "temp")

            shadow = ShadowStorageStrategy(
                strategy,
                _shadow,
                [
                    ResizeMiddleware(2, 2),
                ],
            )

            self.assertFalse(shadow.exists("kagami.png"))
            PIL.Image.new("RGBA", (4, 4), (255, 255, 255, 255)).save(
                tdir / "main" / "kagami.png"
            )
            self.assertTrue(shadow.exists("kagami.png"))

            shadow50 = PIL.Image.open(shadow.get("kagami.png").path).tobytes()
            wanted50 = PIL.Image.new("RGBA", (2, 2), (255, 255, 255, 255)).tobytes()

            self.assertEqual(wanted50, shadow50)

            PIL.Image.new("RGBA", (4, 4), (0, 0, 0, 255)).save(
                tdir / "main" / "kagami.png"
            )
            shadow50 = PIL.Image.open(shadow.get("kagami.png").path).tobytes()
            self.assertNotEqual(wanted50, shadow50)
            wanted50 = PIL.Image.new("RGBA", (2, 2), (0, 0, 0, 255)).tobytes()
            self.assertEqual(wanted50, shadow50)

    def test_fallback(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tpath = Path(tempdir) / "test"
            tpath.write_bytes(b"Hello, world!")
            fallback = JustFallBackStorageStrategy(tpath)
            self.assertTrue(fallback.exists("123"))
            self.assertEqual(fallback.get("456").path, tpath)

    def test_filtered(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir)
            strategy = FilteredStorageStrategy(
                FileStorageStrategy(path), WithPrefixFilter("pre_")
            )
            (path / "npre_123").write_bytes(b"123123")
            (path / "pre_456").write_bytes(b"456456")
            self.assertTrue(strategy.exists("pre_456"))
            self.assertFalse(strategy.exists("npre_123"))
            self.assertFalse(strategy.exists("pre_123"))
            self.assertFalse(strategy.can_put("pree_123"))
            self.assertTrue(strategy.can_put("pre_457"))

    def test_combined(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir)

            (path / "base3").mkdir()
            (path / "base3" / "tmp_234").write_bytes(b"114")
            (path / "base3" / "other_345").write_bytes(b"2341")

            strategy1 = FilteredStorageStrategy(
                FileStorageStrategy(path / "base1"), WithPrefixFilter("tmp_")
            )
            strategy2 = FilteredStorageStrategy(
                FileStorageStrategy(path / "base2"), WithSuffixFilter("qwe")
            )
            strategy3 = StaticStorageStrategy(path / "base3")

            strategy = CombinedStorageStrategy([strategy1, strategy2, strategy3])

            strategy1.put("tmp_123", b"123123")

            self.assertTrue(strategy.exists("tmp_123"))
            self.assertTrue(strategy.exists("tmp_234"))
            self.assertFalse(strategy.exists("tmp_2345"))
            self.assertTrue(strategy.exists("other_345"))
            self.assertFalse(strategy.exists("other_456"))

            strategy.put("tmp_345", b"333")
            self.assertTrue(strategy1.exists("tmp_345"))
            self.assertFalse(strategy2.exists("tmp_345"))

            strategy.put("qweqwe", b"999")
            self.assertFalse(strategy1.exists("qweqwe"))
            self.assertTrue(strategy2.exists("qweqwe"))

            with self.assertRaises(ValueError):
                strategy.put("something_else", b"123123")
