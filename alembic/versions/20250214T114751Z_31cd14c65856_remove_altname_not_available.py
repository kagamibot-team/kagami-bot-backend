"""remove altname not available

Revision ID: 31cd14c65856
Revises: 23317670dced
Create Date: 2025-02-14 11:47:51.190281

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "31cd14c65856"
down_revision: Union[str, None] = "23317670dced"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 本次迁移只删除奇怪的别名

    op.execute(
        "DELETE FROM catch_award_alt_name "
        "WHERE award_id IN ("
        "    SELECT catch_award_alt_name.award_id FROM catch_award_alt_name "
        "    INNER JOIN catch_award "
        "    ON catch_award.data_id = catch_award_alt_name.award_id "
        "    WHERE UPPER(catch_award.name) = UPPER(catch_award_alt_name.name)"
        ");"
    )

    op.execute(
        "DELETE FROM catch_skin_alt_name "
        "WHERE skin_id IN ("
        "    SELECT catch_skin_alt_name.skin_id FROM catch_skin_alt_name "
        "    INNER JOIN catch_skin "
        "    ON catch_skin.data_id = catch_skin_alt_name.skin_id "
        "    WHERE UPPER(catch_skin.name) = UPPER(catch_skin_alt_name.name)"
        ");"
    )

    # 删除 catch_award_alt_name 中大写重名的记录，只保留一个
    op.execute(
        "WITH RankedCatchAwardAltName AS ( "
        "    SELECT  "
        "        data_id, "
        "        ROW_NUMBER() OVER (PARTITION BY UPPER(name) ORDER BY data_id) AS rn "
        "    FROM catch_award_alt_name "
        ") "
        "DELETE FROM catch_award_alt_name "
        "WHERE data_id IN ( "
        "    SELECT data_id FROM RankedCatchAwardAltName WHERE rn > 1 "
        "); "
    )

    # 删除 catch_skin_alt_name 中大写重名的记录，只保留一个
    op.execute(
        "WITH RankedCatchSkinAltName AS ( "
        "    SELECT  "
        "        data_id, "
        "        ROW_NUMBER() OVER (PARTITION BY UPPER(name) ORDER BY data_id) AS rn "
        "    FROM catch_skin_alt_name "
        ") "
        "DELETE FROM catch_skin_alt_name "
        "WHERE data_id IN ( "
        "    SELECT data_id FROM RankedCatchSkinAltName WHERE rn > 1 "
        "); "
    )


def downgrade() -> None:
    pass
