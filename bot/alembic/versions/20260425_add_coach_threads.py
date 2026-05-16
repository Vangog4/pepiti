"""add_coach_threads

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-04-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e4f5a6b7c8d9'
down_revision: Union[str, None] = 'd3e4f5a6b7c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'coach_threads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('messages_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_coach_threads_user_id', 'coach_threads', ['user_id'])
    op.create_index('ix_coach_threads_user_status', 'coach_threads', ['user_id', 'status'])

    op.add_column('users', sa.Column('active_coach_thread_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_users_active_coach_thread',
        'users', 'coach_threads',
        ['active_coach_thread_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_active_coach_thread', 'users', type_='foreignkey')
    op.drop_column('users', 'active_coach_thread_id')
    op.drop_index('ix_coach_threads_user_status', table_name='coach_threads')
    op.drop_index('ix_coach_threads_user_id', table_name='coach_threads')
    op.drop_table('coach_threads')
