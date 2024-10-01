"""
此文件维护了各类对话等信息

国庆活动期间，暂时不启用，很有可能来不及写完
"""

import functools
from pathlib import Path
from random import Random

from pydantic import BaseModel

from src.base.localstorage import LocalStorage, LocalStorageContext
from src.ui.types.liechang import DialogueMessage
from src.ui.types.recipe import MergeData


class MergeDialogData(BaseModel):
    normal: dict[str, dict[str, list[DialogueMessage]]] = {}
    xiaohua: list[DialogueMessage] = []
    love: list[DialogueMessage] = []
    aqu: list[DialogueMessage] = []


class MergeDialogData2(BaseModel):
    l0: list[DialogueMessage] = []
    l1: list[DialogueMessage] = []
    l2: list[DialogueMessage] = []
    l3: list[DialogueMessage] = []
    l4: list[DialogueMessage] = []
    l5: list[DialogueMessage] = []
    baba: list[DialogueMessage] = []
    aqu: list[DialogueMessage] = []
    kl: list[DialogueMessage] = []
    hua: list[DialogueMessage] = []
    lqr: list[DialogueMessage] = []


class DialogData(BaseModel):
    merge: MergeDialogData = MergeDialogData()
    merge_hua_out: MergeDialogData2 = MergeDialogData2()


def local_dialog() -> LocalStorageContext[DialogData]:
    """
    获得本地的对话数据
    """
    return LocalStorage(Path("./data/dialog.json")).context("dialog_data", DialogData)


async def add_merge_dialogue(data: MergeData, random: Random = Random()):
    async with local_dialog() as dialogs:
        if random.random() < 0.1:
            pool = dialogs.merge.aqu
        elif data.output.info.aid == 9:
            pool = dialogs.merge.xiaohua
        elif data.output.info.aid in (34, 98):
            pool = dialogs.merge.love
        else:
            max_input = max(map(lambda x: x.level.lid, data.inputs))
            output = data.output.info.level.lid
            pool = dialogs.merge.normal.get(str(max_input), {}).get(str(output), [])
        if len(pool) == 0 or functools.reduce(
            lambda x, y: x or y,
            map(
                lambda x: x.level.lid == 0 and x.aid != 89,
                [*data.inputs, data.output.info],
            ),
        ):
            pool = [DialogueMessage(text="……", speaker="研究员华", face="黑化")]
        data.dialog = random.choice(pool)
