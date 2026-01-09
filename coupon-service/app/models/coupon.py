from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.enums import CouponState


class Coupon(Base):
    """Coupon model - code is the primary key"""
    __tablename__ = "coupons"
    
    code = Column(String(50), primary_key=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False, index=True)
    assigned_user_id = Column(String, ForeignKey("users.user_id"), nullable=True, index=True)
    state = Column(String(20), default='UNASSIGNED', nullable=False, index=True)
    
    # Multi-redemption support
    redemption_count = Column(Integer, default=0, nullable=False)
    max_redemptions = Column(Integer, default=1, nullable=False)
    
    # Locking (tracked for visibility, actual lock is PostgreSQL advisory)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    book = relationship("Book", back_populates="coupons")
    assigned_user = relationship("User", back_populates="coupons")
    redemption_history = relationship("RedemptionHistory", back_populates="coupon", cascade="all, delete-orphan", lazy="selectin")
    
    def __repr__(self):
        return f"<Coupon(code={self.code}, state={self.state})>"
    
    @property
    def has_redemptions_remaining(self) -> bool:
        """Check if coupon has redemptions remaining"""
        return self.redemption_count < self.max_redemptions
    
    @property
    def remaining_redemptions(self) -> int:
        """Get number of remaining redemptions"""
        return max(0, self.max_redemptions - self.redemption_count)
