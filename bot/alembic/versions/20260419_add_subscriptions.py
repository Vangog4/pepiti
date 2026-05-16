"""add_subscriptions

Revision ID: b1c2d3e4f5a6
Revises: 97ce4ed811de
Create Date: 2026-04-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = '97ce4ed811de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_code', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('telegram_payment_charge_id', sa.String(), nullable=True),
        sa.Column('starts_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
