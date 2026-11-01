"""health calendar events

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-11-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: str | None = "b8c9d0e1f2a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "health_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "pet_id", sa.Integer(), sa.ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("done_at", sa.Date(), nullable=False),
        sa.Column("next_due_at", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("last_notified_on", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_health_events_pet_id", "health_events", ["pet_id"])
    op.create_index("ix_health_events_next_due_at", "health_events", ["next_due_at"])


def downgrade() -> None:
    op.drop_index("ix_health_events_next_due_at", table_name="health_events")
    op.drop_index("ix_health_events_pet_id", table_name="health_events")
    op.drop_table("health_events")
