"""MOVE IMAGES TO NEW FORMAT

Revision ID: 154c643bb1fe
Revises: 38e7597b65a9
Create Date: 2024-10-23 22:12:21.064815

"""

from pathlib import Path
from typing import Sequence, Union

import re

# revision identifiers, used by Alembic.
revision: str = "154c643bb1fe"
down_revision: Union[str, None] = "38e7597b65a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


award_root = Path("./data/awards")
skin_root = Path("./data/skins")


def upgrade() -> None:
    for award in award_root.iterdir():
        if award.is_file():
            name = award.name
            # 匹配 \d_\d.png 的格式，捕捉两个数字

            match = re.match(r"(\d+)_(\d+)\.png", name)
            if match:
                # 第二组丢掉，改成 aid_\d.png
                award.rename(award_root / f"aid_{match.group(1)}.png")

    for skin in skin_root.iterdir():
        if skin.is_file():
            name = skin.name
            # 匹配 \d_\d.png 的格式，捕捉两个数字

            match = re.match(r"(\d+)_(\d+)\.png", name)
            if match:
                # 第二组丢掉，改成 sid_\d.png
                skin.rename(skin_root / f"sid_{match.group(1)}.png")


def downgrade() -> None:
    # 把上面的操作倒过来
    for award in award_root.iterdir():
        if award.is_file():
            name = award.name
            # 匹配 aid_\d.png 的格式，捕捉一个数字

            match = re.match(r"aid_(\d+)\.png", name)
            if match:
                # 把 aid_ 去掉，改成 \d_0.png
                award.rename(award_root / f"{match.group(1)}_0.png")

    for skin in skin_root.iterdir():
        if skin.is_file():
            name = skin.name
            # 匹配 sid_\d.png 的格式，捕捉一个数字

            match = re.match(r"sid_(\d+)\.png", name)
            if match:
                # 把 sid_ 去掉，改成 \d_0.png
                skin.rename(skin_root / f"{match.group(1)}_0.png")
