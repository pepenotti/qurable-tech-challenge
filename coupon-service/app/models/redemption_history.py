from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class RedemptionHistory(Base):
    """Redemption History model for audit trail"""
    __tablename__ = "redemption_history"
    
    history_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), ForeignKey("coupons.code"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    book_id = Column(String, ForeignKey("books.book_id"), nullable=False, index=True)
    redeemed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    redemption_metadata = Column(JSON, nullable=True)  # Store order_id, discount_amount, etc.
    
    # Relationships
    coupon = relationship("Coupon", back_populates="redemption_history")
    user = relationship("User", back_populates="redemption_history")
    
    def __repr__(self):
        return f"<RedemptionHistory(history_id={self.history_id}, code={self.code})>"
