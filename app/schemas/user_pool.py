"""
Pydantic schemas for User Pool management
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserPoolCreate(BaseModel):
    """Schema for creating a new user pool"""
    name: str = Field(..., min_length=1, max_length=200, description="Pool name")
    description: Optional[str] = Field(None, max_length=1000, description="Pool description")
    user_ids: List[str] = Field(default_factory=list, description="Initial list of user IDs to add to pool")


class UserPoolUpdate(BaseModel):
    """Schema for updating a user pool"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UserPoolResponse(BaseModel):
    """Schema for user pool response"""
    pool_id: str
    name: str
    description: Optional[str]
    created_by: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    user_count: int = Field(..., description="Number of users in pool")
    
    class Config:
        from_attributes = True


class UserPoolDetailResponse(UserPoolResponse):
    """Detailed pool response with user list"""
    user_ids: List[str] = Field(..., description="List of user IDs in pool")


class AddUsersToPoolRequest(BaseModel):
    """Request to add users to a pool"""
    user_ids: List[str] = Field(..., min_items=1, description="User IDs to add")


class RemoveUsersFromPoolRequest(BaseModel):
    """Request to remove users from a pool"""
    user_ids: List[str] = Field(..., min_items=1, description="User IDs to remove")


class BulkAssignCouponsRequest(BaseModel):
    """Request to bulk assign coupons from a book to a user pool"""
    book_id: str = Field(..., description="Book ID to assign coupons from")
    pool_id: str = Field(..., description="User pool ID")
    distribution_mode: str = Field(
        default="random",
        description="Distribution mode: 'random' (random distribution) or 'equal' (equal distribution)"
    )
    coupons_per_user: Optional[int] = Field(
        default=1,
        ge=1,
        description="Number of coupons per user (for equal distribution)"
    )


class BulkAssignmentResponse(BaseModel):
    """Response for bulk coupon assignment"""
    success: bool
    total_assigned: int
    assignments: dict = Field(..., description="Map of user_id -> list of assigned codes")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
