"""yet another rename

迁移 ID: 50ed2ee59be6
父迁移: 4572f9f0920f
创建时间: 2024-06-11 14:24:08.208633

"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '50ed2ee59be6'
down_revision: str | Sequence[str] | None = '4572f9f0920f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_award_counter', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('count', sa.Integer(), nullable=False))
        # batch_op.drop_column('award_count')
        batch_op.alter_column('award_count', new_column_name='count')

    with op.batch_alter_table('catch_award_stats', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('count', sa.Integer(), nullable=False))
        # batch_op.drop_column('award_count')
        batch_op.alter_column('award_count', new_column_name='count')

    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_award_stats', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('award_count', sa.INTEGER(), nullable=False))
        # batch_op.drop_column('count')
        batch_op.alter_column('count', new_column_name='award_count')

    with op.batch_alter_table('catch_award_counter', schema=None) as batch_op:
        # batch_op.add_column(sa.Column('award_count', sa.INTEGER(), nullable=False))
        # batch_op.drop_column('count')
        batch_op.alter_column('count', new_column_name='award_count')

    # ### end Alembic commands ###
