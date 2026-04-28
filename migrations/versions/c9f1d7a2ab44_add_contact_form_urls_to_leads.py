"""add contact form urls field to leads

Revision ID: c9f1d7a2ab44
Revises: b1f4d7c9e2aa
Create Date: 2026-04-28 16:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c9f1d7a2ab44"
down_revision = "b1f4d7c9e2aa"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "contact_form_urls", sa.JSON(), nullable=False, server_default="[]"
            )
        )

    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.alter_column("contact_form_urls", server_default=None)


def downgrade():
    with op.batch_alter_table("leads", schema=None) as batch_op:
        batch_op.drop_column("contact_form_urls")
