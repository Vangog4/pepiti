"""weight log

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-11-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b4c5d6e7f8a9"
down_revision: str | None = "a3b4c5d6e7f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "weight_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "pet_id", sa.Integer(), sa.ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_weight_log_pet_id", "weight_log", ["pet_id"])
    op.create_index("ix_weight_log_local_date", "weight_log", ["local_date"])


def downgrade() -> None:
    op.drop_index("ix_weight_log_local_date", table_name="weight_log")
    op.drop_index("ix_weight_log_pet_id", table_name="weight_log")
    op.drop_table("weight_log")
