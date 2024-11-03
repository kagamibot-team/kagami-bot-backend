from pathlib import Path
from unittest import TestCase

from src.base.res.strategy import JustFallBackStorageStrategy


class TestStaticResources(TestCase):
    def assertHave(self, path: Path):
        self.assertTrue(path.exists(), f"Resource {path} does not exist")
        self.assertTrue(path.is_file(), f"Resource {path} is not a file")
        self.assertTrue(path.stat().st_size > 0, f"Resource {path} is empty")
        self.assertTrue(
            JustFallBackStorageStrategy(path).exists(""),
            f"Fallback strategy cannot handle {path} correctly",
        )

    def test_static_resources(self):
        # 测试静态资源是否正常加载
        self.assertHave(Path("./res/default.png"))
        self.assertHave(Path("./res/blank_placeholder.png"))
