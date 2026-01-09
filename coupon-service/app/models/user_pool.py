"""
User Pool model for grouping users and bulk coupon assignment
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


# Association table for many-to-many relationship between pools and users
pool_users = Table(
    'pool_users',
    Base.metadata,
    Column('pool_id', String, ForeignKey('user_pools.pool_id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    Column('added_at', DateTime, server_default=func.now())
)


class UserPool(Base):
    """User pool for bulk coupon distribution"""
    __tablename__ = 'user_pools'
    
    pool_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey('users.user_id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    users = relationship('User', secondary=pool_users, back_populates='pools')
    creator = relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<UserPool(id={self.pool_id}, name={self.name}, users={len(self.users)})>"
