"""unique payment charge id

Revision ID: a7b8c9d0e1f2
Revises: f1a2b3c4d5e6
Create Date: 2026-11-01
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_subscriptions_charge_id",
        "subscriptions",
        ["telegram_payment_charge_id"],
        unique=True,
        postgresql_where="telegram_payment_charge_id IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_index("uq_subscriptions_charge_id", table_name="subscriptions")
