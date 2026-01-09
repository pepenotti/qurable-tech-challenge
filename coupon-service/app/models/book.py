from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Book(Base):
    """Coupon Book model"""
    __tablename__ = "books"
    
    book_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expiration_date = Column(DateTime(timezone=True))
    
    # Configuration
    allow_multi_redemption = Column(Boolean, default=False, nullable=False)
    max_redemptions_per_user = Column(Integer, default=1, nullable=False)
    max_assignments_per_user = Column(Integer, nullable=True)
    code_pattern = Column(String, nullable=True)
    total_code_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="books")
    coupons = relationship("Coupon", back_populates="book", cascade="all, delete-orphan", lazy="selectin")
    
    def __repr__(self):
        return f"<Book(book_id={self.book_id}, name={self.name})>"
