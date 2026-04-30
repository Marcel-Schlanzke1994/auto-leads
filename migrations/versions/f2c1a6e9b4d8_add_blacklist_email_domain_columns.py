"""add blacklist email and domain columns

Revision ID: f2c1a6e9b4d8
Revises: e7b9c2d4f1a6
Create Date: 2026-04-28 23:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2c1a6e9b4d8"
down_revision = "e7b9c2d4f1a6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("blacklists", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("domain", sa.String(length=255), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_blacklists_email"), ["email"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_blacklists_domain"), ["domain"], unique=False
        )


def downgrade():
    with op.batch_alter_table("blacklists", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_blacklists_domain"))
        batch_op.drop_index(batch_op.f("ix_blacklists_email"))
        batch_op.drop_column("domain")
        batch_op.drop_column("email")
