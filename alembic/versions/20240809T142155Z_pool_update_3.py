"""pool update 3

Revision ID: 20240809T142155Z
Revises: 20240809T073627Z
Create Date: 2024-08-09 22:21:59.180042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240809T142155Z'
down_revision: Union[str, None] = '20240809T073627Z'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('catch_up_pool_inventory',
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('pool_id', sa.Integer(), nullable=True),
    sa.Column('data_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['pool_id'], ['catch_up_pool.data_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uid'], ['catch_user_data.data_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('data_id')
    )
    with op.batch_alter_table('catch_up_pool_inventory', schema=None) as batch_op:
        batch_op.create_index('catch_up_pool_inventory_index', ['uid', 'pool_id'], unique=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('catch_up_pool_inventory', schema=None) as batch_op:
        batch_op.drop_index('catch_up_pool_inventory_index')

    op.drop_table('catch_up_pool_inventory')
    # ### end Alembic commands ###
