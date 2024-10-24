"""
和存档文件有关的处理，便于在开发者群聊中同步存档数据
"""

import asyncio
import os
import pathlib
import zipfile

from src.common.times import now_datetime


def move_file(src: pathlib.Path, dst: pathlib.Path):
    """
    移动文件，如果目标文件夹不存在则创建
    """

    if not os.path.exists(dst.parent):
        os.mkdir(dst.parent)

    # 使用文件读写
    with open(src, "rb") as f:
        with open(dst, "wb") as f2:
            f2.write(f.read())

    # 删除源文件
    try:
        os.remove(src)
    except PermissionError:
        pass


def pack_save_task(zfp: pathlib.Path):
    with zipfile.ZipFile(zfp, "w") as zf:
        zf.mkdir("data/")
        zf.mkdir("data/awards/")
        for fp in pathlib.Path("./data/awards/").iterdir():
            fn = fp.name
            with zf.open(f"data/awards/{fn}", "w") as f:
                f.write(fp.read_bytes())

        zf.mkdir("data/skins/")
        for fp in pathlib.Path("./data/skins/").iterdir():
            fn = fp.name
            with zf.open(f"data/skins/{fn}", "w") as f:
                f.write(fp.read_bytes())

        with zf.open("data/db.sqlite3", "w") as f:
            f.write(pathlib.Path("./data/db.sqlite3").read_bytes())

        with zf.open("data/localstorage.json", "w") as f:
            f.write(pathlib.Path("./data/localstorage.json").read_bytes())

        with zf.open("data/log.log", "w") as f:
            f.write(pathlib.Path("./data/log.log").read_bytes())


async def pack_save(filename: str | None = None):
    """把游戏存档打包成压缩包

    Args:
        filename (str | None, optional): 压缩包的名字. Defaults to None.

    Returns:
        Path: 压缩包存到了哪里
    """
    # await collect_images()

    filename = filename or f"save-{now_datetime().strftime('%Y-%m-%dT%H_%M_%S')}.zip"
    fp = pathlib.Path("./data/backup/") / filename
    await asyncio.get_event_loop().run_in_executor(None, pack_save_task, fp)

    return fp
