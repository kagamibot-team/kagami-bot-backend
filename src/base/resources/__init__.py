import hashlib
from pathlib import Path

import PIL
import PIL.Image
from pydantic import BaseModel


class Resource(BaseModel):
    """
    资源文件
    """

    path: Path
    url: str

    def read_bytes(self):
        return self.path.read_bytes()

    def get_hash(self):
        return hashlib.sha256(self.read_bytes()).hexdigest()

    def get_pillow_image(self):
        return PIL.Image.open(self.path)

    def compress_image(self, width: int | None = None, height: int | None = None):
        """
        获得压缩后的图像
        """
        # 把不符合条件的值清楚
        if width is not None and width <= 0:
            width = None
        if height is not None and height <= 0:
            height = None
            
        # 生成文件名
        fn = self.get_hash()
        if width is not None:
            fn += f"_x{width}"
        if height is not None:
            fn += f"_y{height}"
        fn = fn + ".webp"
        res = temp_res(fn)

        # 之前生成过就不生成啦
        if res.path.exists():
            return res

        # 生成 webp 压缩后的图像
        img = self.get_pillow_image()
        if width is None and height is not None:
            width = int(img.width / img.height * height)
            width = max(1, width)
        if width is not None and height is None:
            height = int(img.height / img.width * width)
            height = max(1, height)
        if width is not None and height is not None:
            img.resize((width, height))
        img.save(res.path, "webp")

        return res


def static_res(name: str):
    """
    静态资源
    """

    return Resource(
        path=Path("./res") / name,
        url=f"/kagami-res/{name}",
    )


def temp_res(name: str):
    """
    临时文件
    """

    return Resource(path=Path("./data") / "temp" / name, url=f"/file/temp/{name}")
