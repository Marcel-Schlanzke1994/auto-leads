"""add notes and scheduling fields for outreach models

Revision ID: d4e8a9f1c2b7
Revises: c9f1d7a2ab44
Create Date: 2026-04-28 20:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d4e8a9f1c2b7"
down_revision = "c9f1d7a2ab44"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("contact_attempts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("notes", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True)
        )

    with op.batch_alter_table("outreach_drafts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("personalization_notes", sa.Text(), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("outreach_drafts", schema=None) as batch_op:
        batch_op.drop_column("personalization_notes")

    with op.batch_alter_table("contact_attempts", schema=None) as batch_op:
        batch_op.drop_column("scheduled_for")
        batch_op.drop_column("notes")
