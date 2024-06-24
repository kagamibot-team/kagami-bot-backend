"""
和存档文件有关的处理，便于在开发者群聊中同步存档数据
"""

import asyncio
import os
import pathlib
import shutil
import zipfile
from sqlalchemy import select, update
from src.base.db import get_session
from src.common.times import now_datetime
from src.models.models import Award, Skin


async def collect_images():
    """
    将图像资源文件整理并置放到对应的文件夹，并将先前的图片文件备份到 Backup 中
    """

    session = get_session()
    async with session.begin():
        query = select(Award.data_id, Award.img_path)
        awards = (await session.execute(query)).tuples()

        folder = pathlib.Path("./data/awards/")
        applied: set[pathlib.Path] = set()

        for did, img in awards:
            img_path = pathlib.Path(img)
            if img_path.parent != folder:
                target_path = folder / f"{did}_0.png"
                if os.path.exists(img_path):
                    shutil.move(img_path, target_path)
                img_path = target_path
                await session.execute(
                    update(Award)
                    .where(Award.data_id == did)
                    .values(img_path=str(img_path))
                )
            applied.add(img_path)

        backup_dir = pathlib.Path("./data/backup/awards/")

        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)

        for fp in folder.iterdir():
            if fp not in applied:
                shutil.move(fp, backup_dir)

        query2 = select(Skin.data_id, Skin.image)
        skins = (await session.execute(query2)).tuples()

        folder = pathlib.Path("./data/skins/")
        applied: set[pathlib.Path] = set()

        for did, img in skins:
            img_path = pathlib.Path(img)
            if img_path.parent != folder:
                target_path = folder / f"{did}_0.png"
                if os.path.exists(img_path):
                    shutil.move(img_path, target_path)
                img_path = target_path
                await session.execute(
                    update(Skin).where(Skin.data_id == did).values(image=str(img_path))
                )
            applied.add(img_path)

        backup_dir = pathlib.Path("./data/backup/skins/")

        if not os.path.exists(backup_dir):
            os.mkdir(backup_dir)

        for fp in folder.iterdir():
            if fp not in applied:
                shutil.move(fp, backup_dir)

        await session.commit()


def pack_save_task(fp: pathlib.Path):
    zf = zipfile.ZipFile(fp, "w")

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

    with zf.open("data/catch_history.json", "w") as f:
        f.write(pathlib.Path("./data/catch_history.json").read_bytes())

    zf.close()


async def pack_save(filename: str | None = None):
    await collect_images()

    filename = filename or f"save-{now_datetime().strftime('%Y-%m-%dT%H_%M_%S')}.zip"
    fp = pathlib.Path("./data/backup/") / filename
    await asyncio.get_event_loop().run_in_executor(None, pack_save_task, fp)

    return fp
