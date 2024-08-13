"""sleep update

Revision ID: 20240813T045654Z
Revises: 20240811T080200Z
Create Date: 2024-08-13 12:56:58.533263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240813T045654Z'
down_revision: Union[str, None] = '20240811T080200Z'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_user_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('get_up_time', sa.Float(), server_default='0', nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_user_data', schema=None) as batch_op:
        batch_op.drop_column('get_up_time')

    # ### end Alembic commands ###
