from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """User model with authentication support"""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    books = relationship("Book", back_populates="owner", lazy="selectin")
    coupons = relationship("Coupon", back_populates="assigned_user", lazy="selectin")
    redemption_history = relationship("RedemptionHistory", back_populates="user", lazy="selectin")
    pools = relationship("UserPool", secondary="pool_users", back_populates="users")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, role={self.role})>"
