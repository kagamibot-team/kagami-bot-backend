"""rebase remove level

Revision ID: 20240711T052226Z
Revises: 0b7c957500dc
Create Date: 2024-07-11 13:22:29.877920

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20240711T052226Z"
down_revision: Union[str, None] = "0b7c957500dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # 这一次的更新最疯狂了，我只能说……

    with op.batch_alter_table("catch_recipe", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("modified", sa.Integer(), server_default="0", nullable=True)
        )

    # Part 1 重命名的一些字段
    with op.batch_alter_table("catch_award", schema=None) as batch_op:
        batch_op.alter_column("img_path", new_column_name="image")
        batch_op.alter_column("sorting_priority", new_column_name="sorting")
        batch_op.drop_index("ix_catch_award_catch_group")
        batch_op.drop_constraint(
            "fk_catch_award_level_id_catch_level", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "fk_catch_award_catch_group_catch_catch_group_data_id", type_="foreignkey"
        )
        batch_op.drop_column("catch_group")

    op.drop_table("catch_catch_group")

    # 库存表合并
    op.rename_table("catch_award_counter", "catch_inventory")
    with op.batch_alter_table("catch_inventory", schema=None) as batch_op:
        batch_op.alter_column("count", new_column_name="storage")
        batch_op.alter_column("target_user_id", new_column_name="user_id")
        batch_op.alter_column("target_award_id", new_column_name="award_id")
        batch_op.add_column(
            sa.Column("used", sa.Integer(), server_default="0", nullable=False)
        )
    op.execute(
        """
        UPDATE catch_inventory
        SET used = catch_award_stats.count
        FROM catch_award_stats
        WHERE catch_award_stats.target_user_id = catch_inventory.user_id
            AND catch_award_stats.target_award_id = catch_inventory.award_id
        """
    )
    op.drop_table("catch_award_stats")

    # 皮肤表合并，这里没办法了，先销掉吧
    op.rename_table("catch_skin_own_record", "catch_skin_inventory")
    with op.batch_alter_table("catch_skin_inventory", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("selected", sa.Integer(), server_default="0", nullable=False)
        )
    op.execute(
        """
        UPDATE catch_skin_inventory
        SET selected = 1
        WHERE EXISTS (
            SELECT 1 FROM catch_skin_record
            WHERE skin_id = catch_skin_inventory.skin_id
        )
        """
    )
    op.drop_table("catch_skin_record")

    ## 删除等级相关的所有东西
    with op.batch_alter_table("catch_level_alt_name", schema=None) as batch_op:
        batch_op.drop_index("ix_catch_level_alt_name_name")
    op.drop_table("catch_level_alt_name")
    op.drop_table("catch_level_tag_relation")
    op.drop_table("catch_level")

    # 调整皮肤表（命名更改）
    with op.batch_alter_table("catch_skin", schema=None) as batch_op:
        batch_op.alter_column("applied_award_id", new_column_name="award_id")
        batch_op.alter_column("extra_description", new_column_name="description")
        batch_op.drop_constraint(
            "fk_catch_skin_applied_award_id_catch_award", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "catch_skin_award_foreignkey",
            "catch_award",
            ["award_id"],
            ["data_id"],
            ondelete="CASCADE",
        )

    # ### end Alembic commands ###


def downgrade() -> None:

    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("catch_skin", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("extra_description", sa.VARCHAR(), nullable=False)
        )
        batch_op.add_column(sa.Column("applied_award_id", sa.INTEGER(), nullable=True))
        batch_op.drop_constraint("catch_skin_award_foreignkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_catch_skin_applied_award_id_catch_award",
            "catch_award",
            ["applied_award_id"],
            ["data_id"],
            ondelete="CASCADE",
        )
        batch_op.drop_column("award_id")
        batch_op.drop_column("description")

    with op.batch_alter_table("catch_recipe", schema=None) as batch_op:
        batch_op.drop_column("modified")

    with op.batch_alter_table("catch_award", schema=None) as batch_op:
        batch_op.add_column(sa.Column("img_path", sa.VARCHAR(), nullable=False))
        batch_op.add_column(sa.Column("catch_group", sa.INTEGER(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "sorting_priority",
                sa.INTEGER(),
                server_default=sa.text("'0'"),
                nullable=False,
            )
        )
        batch_op.create_foreign_key(
            "fk_catch_award_catch_group_catch_catch_group_data_id",
            "catch_catch_group",
            ["catch_group"],
            ["data_id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_catch_award_level_id_catch_level",
            "catch_level",
            ["level_id"],
            ["data_id"],
            ondelete="CASCADE",
        )
        batch_op.create_index(
            "ix_catch_award_catch_group", ["catch_group"], unique=False
        )
        batch_op.drop_column("sorting")
        batch_op.drop_column("image")

    op.create_table(
        "catch_level",
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("weight", sa.FLOAT(), nullable=False),  # type: ignore
        sa.Column("color_code", sa.VARCHAR(), nullable=False),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.Column("price", sa.FLOAT(), server_default=sa.text("'0.0'"), nullable=False),  # type: ignore
        sa.Column(
            "sorting_priority",
            sa.INTEGER(),
            server_default=sa.text("'0'"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_level"),
        sa.UniqueConstraint("name", name="uq_catch_level_name"),
    )
    op.create_table(
        "catch_level_tag_relation",
        sa.Column("level_id", sa.INTEGER(), nullable=True),
        sa.Column("tag_id", sa.INTEGER(), nullable=True),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(
            ["level_id"],
            ["catch_level.data_id"],
            name="fk_catch_level_tag_relation_level_id_catch_level",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["catch_tag.data_id"],
            name="fk_catch_level_tag_relation_tag_id_catch_tag",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_level_tag_relation"),
    )
    op.create_table(
        "catch_skin_record",
        sa.Column("user_id", sa.INTEGER(), nullable=True),
        sa.Column("skin_id", sa.INTEGER(), nullable=True),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skin_id"],
            ["catch_skin.data_id"],
            name="fk_catch_skin_record_skin_id_catch_skin",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["catch_user_data.data_id"],
            name="fk_catch_skin_record_user_id_catch_user_data",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_skin_record"),
    )
    op.create_table(
        "catch_award_counter",
        sa.Column("target_user_id", sa.INTEGER(), nullable=True),
        sa.Column("target_award_id", sa.INTEGER(), nullable=True),
        sa.Column("count", sa.INTEGER(), nullable=False),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(
            ["target_award_id"],
            ["catch_award.data_id"],
            name="fk_catch_award_counter_target_award_id_catch_award",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"],
            ["catch_user_data.data_id"],
            name="fk_catch_award_counter_target_user_id_catch_user_data",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_award_counter"),
    )
    with op.batch_alter_table("catch_award_counter", schema=None) as batch_op:
        batch_op.create_index(
            "storage_stat_index", ["target_user_id", "target_award_id"], unique=1
        )

    op.create_table(
        "catch_level_alt_name",
        sa.Column("level_id", sa.INTEGER(), nullable=True),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.ForeignKeyConstraint(
            ["level_id"],
            ["catch_level.data_id"],
            name="fk_catch_level_alt_name_level_id_catch_level",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_level_alt_name"),
        sa.UniqueConstraint("name"),
    )
    with op.batch_alter_table("catch_level_alt_name", schema=None) as batch_op:
        batch_op.create_index("ix_catch_level_alt_name_name", ["name"], unique=1)

    op.create_table(
        "catch_skin_own_record",
        sa.Column("user_id", sa.INTEGER(), nullable=True),
        sa.Column("skin_id", sa.INTEGER(), nullable=True),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skin_id"],
            ["catch_skin.data_id"],
            name="fk_catch_skin_own_record_skin_id_catch_skin",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["catch_user_data.data_id"],
            name="fk_catch_skin_own_record_user_id_catch_user_data",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_skin_own_record"),
    )
    op.create_table(
        "catch_award_stats",
        sa.Column("target_user_id", sa.INTEGER(), nullable=True),
        sa.Column("target_award_id", sa.INTEGER(), nullable=True),
        sa.Column("count", sa.INTEGER(), nullable=False),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(
            ["target_award_id"],
            ["catch_award.data_id"],
            name="fk_catch_award_stats_target_award_id_catch_award",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"],
            ["catch_user_data.data_id"],
            name="fk_catch_award_stats_target_user_id_catch_user_data",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("data_id", name="pk_catch_award_stats"),
    )
    op.create_table(
        "catch_catch_group",
        sa.Column("weight", sa.FLOAT(), server_default=sa.text("'0'"), nullable=False),  # type: ignore
        sa.Column("time_limit_rule", sa.VARCHAR(), nullable=False),
        sa.Column("data_id", sa.INTEGER(), nullable=False),
        sa.Column("created_at", sa.DATETIME(), nullable=False),
        sa.Column("updated_at", sa.DATETIME(), nullable=False),
        sa.PrimaryKeyConstraint("data_id"),
    )
    op.drop_table("catch_skin_inventory")
    with op.batch_alter_table("catch_inventory", schema=None) as batch_op:
        batch_op.drop_index("storage_stat_index")

    op.drop_table("catch_inventory")
    # ### end Alembic commands ###
