"""add outreach and compliance models

Revision ID: b1f4d7c9e2aa
Revises: a3d2f8e1b9c4
Create Date: 2026-04-28 15:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1f4d7c9e2aa"
down_revision = "a3d2f8e1b9c4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "contact_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("recipient", sa.String(length=255), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_summary", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("contact_attempts", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_contact_attempts_channel"), ["channel"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_contact_attempts_direction"), ["direction"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_contact_attempts_lead_id"), ["lead_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_contact_attempts_recipient"), ["recipient"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_contact_attempts_status"), ["status"], unique=False
        )

    op.create_table(
        "outreach_drafts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("template_key", sa.String(length=120), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("tone", sa.String(length=50), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("outreach_drafts", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_outreach_drafts_channel"), ["channel"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_outreach_drafts_language"), ["language"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_outreach_drafts_lead_id"), ["lead_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_outreach_drafts_status"), ["status"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_outreach_drafts_template_key"),
            ["template_key"],
            unique=False,
        )

    op.create_table(
        "opt_outs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("email_normalized", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("phone_normalized", sa.String(length=40), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("opt_outs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_opt_outs_channel"), ["channel"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_opt_outs_domain"), ["domain"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_opt_outs_email"), ["email"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_opt_outs_email_normalized"),
            ["email_normalized"],
            unique=False,
        )
        batch_op.create_index(batch_op.f("ix_opt_outs_phone"), ["phone"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_opt_outs_phone_normalized"),
            ["phone_normalized"],
            unique=False,
        )

    op.create_table(
        "blacklists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.String(length=20), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("value_normalized", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "entry_type", "value", name="uq_blacklists_entry_type_value"
        ),
    )
    with op.batch_alter_table("blacklists", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_blacklists_active"), ["active"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_blacklists_entry_type"), ["entry_type"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_blacklists_value"), ["value"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_blacklists_value_normalized"),
            ["value_normalized"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("blacklists", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_blacklists_value_normalized"))
        batch_op.drop_index(batch_op.f("ix_blacklists_value"))
        batch_op.drop_index(batch_op.f("ix_blacklists_entry_type"))
        batch_op.drop_index(batch_op.f("ix_blacklists_active"))

    op.drop_table("blacklists")

    with op.batch_alter_table("opt_outs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_opt_outs_phone_normalized"))
        batch_op.drop_index(batch_op.f("ix_opt_outs_phone"))
        batch_op.drop_index(batch_op.f("ix_opt_outs_email_normalized"))
        batch_op.drop_index(batch_op.f("ix_opt_outs_email"))
        batch_op.drop_index(batch_op.f("ix_opt_outs_domain"))
        batch_op.drop_index(batch_op.f("ix_opt_outs_channel"))

    op.drop_table("opt_outs")

    with op.batch_alter_table("outreach_drafts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_outreach_drafts_template_key"))
        batch_op.drop_index(batch_op.f("ix_outreach_drafts_status"))
        batch_op.drop_index(batch_op.f("ix_outreach_drafts_lead_id"))
        batch_op.drop_index(batch_op.f("ix_outreach_drafts_language"))
        batch_op.drop_index(batch_op.f("ix_outreach_drafts_channel"))

    op.drop_table("outreach_drafts")

    with op.batch_alter_table("contact_attempts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_contact_attempts_status"))
        batch_op.drop_index(batch_op.f("ix_contact_attempts_recipient"))
        batch_op.drop_index(batch_op.f("ix_contact_attempts_lead_id"))
        batch_op.drop_index(batch_op.f("ix_contact_attempts_direction"))
        batch_op.drop_index(batch_op.f("ix_contact_attempts_channel"))

    op.drop_table("contact_attempts")
