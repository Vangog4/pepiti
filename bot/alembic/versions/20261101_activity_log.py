"""activity log (tracker) and weekly report marker

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-11-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: str | None = "c9d0e1f2a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "activity_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "pet_id", sa.Integer(), sa.ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_activity_log_pet_id", "activity_log", ["pet_id"])
    op.create_index("ix_activity_log_local_date", "activity_log", ["local_date"])
    op.add_column("users", sa.Column("weekly_report_sent_on", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "weekly_report_sent_on")
    op.drop_index("ix_activity_log_local_date", table_name="activity_log")
    op.drop_index("ix_activity_log_pet_id", table_name="activity_log")
    op.drop_table("activity_log")
