import tempfile
from pathlib import Path
from unittest import TestCase

from pydantic import BaseModel, ValidationError

from src.base.localstorage import LocalStorage


class ModelA(BaseModel):
    boolean_value: bool = False


class ModelB(BaseModel):
    boolean_value: bool = False
    int_value: int = 0


class TestBaseFunction(TestCase):
    def test_basic_function(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            fp = base / "test.json"
            ls = LocalStorage(fp)

            # 测试数据的获取
            item = ls.get_item("test", ModelA)
            self.assertFalse(item.boolean_value)

            # 测试数据的只读性
            item.boolean_value = True
            item = ls.get_item("test", ModelA)
            self.assertFalse(item.boolean_value)

            # 测试数据的写入
            item = ls.get_item("test2", ModelA)
            item.boolean_value = True
            ls.set_item("test2", item)
            item = ls.get_item("test2", ModelA)
            self.assertTrue(item.boolean_value)

            # 测试数据的持久性
            ls2 = LocalStorage(fp)
            item = ls2.get_item("test2", ModelA)
            self.assertTrue(item.boolean_value)

            # 测试数据的升级
            item = ls.get_item("test2", ModelB)
            self.assertTrue(item.boolean_value)
            self.assertEqual(item.int_value, 0)

            # 测试上下文
            with ls.context("test10", ModelB) as data:
                data.boolean_value = True
                data.int_value = 114

            with ls2.context("test10", ModelB) as data:
                self.assertTrue(data.boolean_value)
                self.assertEqual(data.int_value, 114)

    def test_exceptions(self):
        with tempfile.TemporaryDirectory() as d:
            # 测试母文件夹不存在时的情况
            base = Path(d) / "testfolder" / "hello"
            fp = base / "test.json"
            ls = LocalStorage(fp)

            # 测试 JSON 读取出错的情况
            with open(fp, "w") as f:
                # 这个肯定是不合法的 JSON 了吧！
                # 哼哼！
                f.write("asiuhvcxvojcxivjasego}{")
            ls.load()

            # 测试数据验证出错
            ls.data["test"] = {"boolean_value": 31}
            ls.write()
            item = ls.get_item("test", ModelA, allow_overwrite=True)
            self.assertFalse(item.boolean_value)

            ls.data["test"] = {"boolean_value": 31}
            ls.write()
            def broken():
                ls.get_item("test", ModelA, allow_overwrite=False)
            self.assertRaises(ValidationError, broken)

            # 测试在处理数据的中途报错
            with ls.context("test2", ModelB) as data:
                data.boolean_value = True
                data.int_value = 42
            def broken2():
                with ls.context("test2", ModelB) as data:
                    data.boolean_value = False
                    data.int_value = 114
                    raise ValueError("test exception")
            self.assertRaises(ValueError, broken2)
            with ls.context("test2", ModelB) as data:
                self.assertTrue(data.boolean_value)
                self.assertEqual(data.int_value, 42)
