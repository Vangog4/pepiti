"""pet passport fields and pet_facts memory

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-11-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: str | None = "a7b8c9d0e1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("pets", sa.Column("birth_date", sa.Date(), nullable=True))
    op.add_column("pets", sa.Column("allergies", postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column(
        "pets", sa.Column("chronic_conditions", postgresql.ARRAY(sa.String()), nullable=True)
    )
    op.add_column("pets", sa.Column("photo_file_id", sa.String(), nullable=True))
    op.add_column(
        "pets",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_table(
        "pet_facts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "pet_id", sa.Integer(), sa.ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("fact", sa.Text(), nullable=False),
        sa.Column("source", sa.String(), nullable=False, server_default="ai"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_pet_facts_pet_id", "pet_facts", ["pet_id"])


def downgrade() -> None:
    op.drop_index("ix_pet_facts_pet_id", table_name="pet_facts")
    op.drop_table("pet_facts")
    for col in ("is_active", "photo_file_id", "chronic_conditions", "allergies", "birth_date"):
        op.drop_column("pets", col)
