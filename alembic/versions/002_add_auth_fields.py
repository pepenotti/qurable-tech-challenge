"""add user authentication fields

Revision ID: 002
Revises: 001
Create Date: 2026-01-07 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=True, server_default='user'))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')))
    
    # For existing users, set a default hashed password and make fields required
    # In production, you would need to handle this differently (e.g., force password reset)
    op.execute("""
        UPDATE users 
        SET hashed_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIvAprzV3i',  -- 'password123'
            role = 'user',
            is_active = true,
            updated_at = now()
        WHERE hashed_password IS NULL
    """)
    
    # Now make columns non-nullable
    op.alter_column('users', 'hashed_password', nullable=False)
    op.alter_column('users', 'role', nullable=False)
    op.alter_column('users', 'is_active', nullable=False)
    op.alter_column('users', 'updated_at', nullable=False)


def downgrade() -> None:
    # Remove added columns
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.drop_column('users', 'hashed_password')
    
    # Drop the enum type
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
