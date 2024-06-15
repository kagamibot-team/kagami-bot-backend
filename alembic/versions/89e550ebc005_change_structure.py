"""change structure

Revision ID: 89e550ebc005
Revises: cd4e2021645a
Create Date: 2024-06-15 16:25:50.016268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89e550ebc005'
down_revision: Union[str, None] = 'cd4e2021645a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_user_data', schema=None) as batch_op:
        batch_op.drop_constraint('uq_catch_user_data_qq_id', type_='unique')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_user_data', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_catch_user_data_qq_id', ['qq_id'])

    # ### end Alembic commands ###
