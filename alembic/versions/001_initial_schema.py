"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table with authentication fields
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create books table
    op.create_table(
        'books',
        sa.Column('book_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allow_multi_redemption', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('max_redemptions_per_user', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('max_assignments_per_user', sa.Integer(), nullable=True),
        sa.Column('code_pattern', sa.String(length=100), nullable=True),
        sa.Column('total_code_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('book_id')
    )
    op.create_index(op.f('ix_books_owner_id'), 'books', ['owner_id'], unique=False)
    
    # Create coupons table
    op.create_table(
        'coupons',
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('book_id', sa.String(), nullable=False),
        sa.Column('assigned_user_id', sa.String(), nullable=True),
        sa.Column('state', sa.String(length=20), nullable=False, server_default='UNASSIGNED'),
        sa.Column('redemption_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('max_redemptions', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_coupons_assigned_user_id'), 'coupons', ['assigned_user_id'], unique=False)
    op.create_index(op.f('ix_coupons_book_id'), 'coupons', ['book_id'], unique=False)
    op.create_index(op.f('ix_coupons_state'), 'coupons', ['state'], unique=False)
    
    # Create redemption_history table
    op.create_table(
        'redemption_history',
        sa.Column('history_id', sa.String(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('book_id', sa.String(), nullable=False),
        sa.Column('redeemed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('redemption_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.book_id'], ),
        sa.ForeignKeyConstraint(['code'], ['coupons.code'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('history_id')
    )
    op.create_index(op.f('ix_redemption_history_code'), 'redemption_history', ['code'], unique=False)
    op.create_index(op.f('ix_redemption_history_redeemed_at'), 'redemption_history', ['redeemed_at'], unique=False)
    op.create_index(op.f('ix_redemption_history_user_id'), 'redemption_history', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_redemption_history_user_id'), table_name='redemption_history')
    op.drop_index(op.f('ix_redemption_history_redeemed_at'), table_name='redemption_history')
    op.drop_index(op.f('ix_redemption_history_code'), table_name='redemption_history')
    op.drop_table('redemption_history')
    
    op.drop_index(op.f('ix_coupons_state'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_book_id'), table_name='coupons')
    op.drop_index(op.f('ix_coupons_assigned_user_id'), table_name='coupons')
    op.drop_table('coupons')
    
    op.drop_index(op.f('ix_books_owner_id'), table_name='books')
    op.drop_table('books')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
