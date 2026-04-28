"""add normalized duplicate detection fields and indexes

Revision ID: a3d2f8e1b9c4
Revises: 6d700b6863f3
Create Date: 2026-04-28 13:25:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3d2f8e1b9c4"
down_revision = "6d700b6863f3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("city_normalized", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("email_normalized", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("phone_normalized", sa.String(length=40), nullable=True)
        )

        batch_op.create_index(
            batch_op.f("ix_leads_city_normalized"), ["city_normalized"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_leads_email_normalized"), ["email_normalized"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_leads_phone_normalized"), ["phone_normalized"], unique=False
        )
        batch_op.create_index(
            "ix_leads_normalized_name_city",
            ["normalized_company_name", "city_normalized"],
            unique=False,
        )

        batch_op.drop_index(batch_op.f("ix_leads_domain"))
        batch_op.create_index(batch_op.f("ix_leads_domain"), ["domain"], unique=True)


def downgrade():
    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.drop_index("ix_leads_normalized_name_city")
        batch_op.drop_index(batch_op.f("ix_leads_phone_normalized"))
        batch_op.drop_index(batch_op.f("ix_leads_email_normalized"))
        batch_op.drop_index(batch_op.f("ix_leads_city_normalized"))

        batch_op.drop_column("phone_normalized")
        batch_op.drop_column("email_normalized")
        batch_op.drop_column("city_normalized")

        batch_op.drop_index(batch_op.f("ix_leads_domain"))
        batch_op.create_index(batch_op.f("ix_leads_domain"), ["domain"], unique=False)
