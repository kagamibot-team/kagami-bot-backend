"""CDKEY UPDATE  2

Revision ID: 2e196e0d18ff
Revises: b6acc95e6ac3
Create Date: 2024-09-16 12:40:14.573882

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2e196e0d18ff"
down_revision: Union[str, None] = "b6acc95e6ac3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "catch_cdk_batch",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("max_redeem_limit", sa.Integer(), nullable=True),
        sa.Column("expiration_date", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("data_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("data_id"),
    )
    op.create_table(
        "catch_cdk_batch_award",
        sa.Column("batch_id", sa.Integer(), nullable=True),
        sa.Column("aid", sa.Integer(), nullable=True),
        sa.Column("sid", sa.Integer(), nullable=True),
        sa.Column("chips", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("data_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["aid"], ["catch_award.data_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["batch_id"], ["catch_cdk_batch.data_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["sid"], ["catch_skin.data_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("data_id"),
    )
    op.drop_table("catch_cdk_award")
    with op.batch_alter_table("catch_cdk", schema=None) as batch_op:
        batch_op.add_column(sa.Column("code", sa.String(), nullable=False))
        batch_op.add_column(sa.Column("batch_id", sa.Integer(), nullable=True))
        batch_op.create_unique_constraint("uq_catch_cdk_code", ["code"])
        batch_op.create_foreign_key(
            "fk_catch_cdk_batch_catch_cdk", "catch_cdk_batch", ["batch_id"], ["data_id"]
        )
        batch_op.drop_column("key")
        batch_op.drop_column("max_uses")
        batch_op.drop_column("is_active")
        batch_op.drop_column("expiration_date")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("catch_cdk", schema=None) as batch_op:
        batch_op.add_column(sa.Column("expiration_date", sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column("is_active", sa.BOOLEAN(), nullable=False))
        batch_op.add_column(sa.Column("max_uses", sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column("key", sa.VARCHAR(), nullable=False))
        batch_op.drop_constraint("fk_catch_cdk_batch_catch_cdk", type_="foreignkey")
        batch_op.drop_constraint("uq_catch_cdk_code", type_="unique")
        batch_op.drop_column("batch_id")
        batch_op.drop_column("code")

    op.create_table(
        "catch_cdk_award",
        sa.Column("cdk_id", sa.INTEGER(), nullable=True),
        sa.Column("aid", sa.INTEGER(), nullable=True),
        sa.Column("sid", sa.INTEGER(), nullable=True),
        sa.Column("chips", sa.INTEGER(), nullable=False),
        sa.Column("quantity", sa.INTEGER(), nullable=False),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(["aid"], ["catch_award.data_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cdk_id"], ["catch_cdk.data_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sid"], ["catch_skin.data_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("data_id"),
    )
    op.drop_table("catch_cdk_batch_award")
    op.drop_table("catch_cdk_batch")
    # ### end Alembic commands ###