"""Add user pools

Revision ID: 002
Revises: 001
Create Date: 2026-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_pools table
    op.create_table(
        'user_pools',
        sa.Column('pool_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('pool_id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_user_pools_created_by'), 'user_pools', ['created_by'], unique=False)
    
    # Create pool_users association table (many-to-many between pools and users)
    op.create_table(
        'pool_users',
        sa.Column('pool_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['pool_id'], ['user_pools.pool_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('pool_id', 'user_id')
    )
    op.create_index(op.f('ix_pool_users_user_id'), 'pool_users', ['user_id'], unique=False)
    op.create_index(op.f('ix_pool_users_pool_id'), 'pool_users', ['pool_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_pool_users_pool_id'), table_name='pool_users')
    op.drop_index(op.f('ix_pool_users_user_id'), table_name='pool_users')
    op.drop_index(op.f('ix_user_pools_created_by'), table_name='user_pools')
    
    # Drop tables
    op.drop_table('pool_users')
    op.drop_table('user_pools')
