"""add company fields to opt outs and blacklists

Revision ID: e7b9c2d4f1a6
Revises: d4e8a9f1c2b7
Create Date: 2026-04-28 22:15:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7b9c2d4f1a6"
down_revision = "d4e8a9f1c2b7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("opt_outs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("company_name", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("company_name_normalized", sa.String(length=255), nullable=True)
        )
        batch_op.create_index(
            batch_op.f("ix_opt_outs_company_name_normalized"),
            ["company_name_normalized"],
            unique=False,
        )

    with op.batch_alter_table("blacklists", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("company_name", sa.String(length=255), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("blacklists", schema=None) as batch_op:
        batch_op.drop_column("company_name")

    with op.batch_alter_table("opt_outs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_opt_outs_company_name_normalized"))
        batch_op.drop_column("company_name_normalized")
        batch_op.drop_column("company_name")
