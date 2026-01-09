"""
Pydantic schemas for request validation and response serialization
"""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from app.utils.enums import CouponState


# ===== Authentication Schemas =====
class UserRegisterRequest(BaseModel):
    """Request schema for user registration"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100, description="Password must be at least 8 characters")


class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    """Request schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ===== User Schemas =====
class UserCreate(BaseModel):
    """Request schema for creating a user (admin only)"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field("user", pattern="^(admin|user)$")


class UserUpdate(BaseModel):
    """Request schema for updating user"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Response schema for a user"""
    user_id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for authentication token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserCouponsResponse(BaseModel):
    """Response schema for user's coupons"""
    user_id: str
    total_count: int
    coupons: list[CouponResponse]


# ===== Book Schemas =====
class CreateBookRequest(BaseModel):
    """Request schema for creating a new coupon book"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    owner_id: str = Field(..., description="User ID of the book owner")
    expiration_date: Optional[datetime] = None
    allow_multi_redemption: bool = False
    max_redemptions_per_user: int = Field(1, ge=1, description="Max redemptions per user")
    max_assignments_per_user: Optional[int] = Field(None, ge=1, description="Max coupons assignable per user")
    code_pattern: Optional[str] = Field(None, description="Pattern for code generation (e.g., 'SUMMER2024-{}')")
    total_code_count: int = Field(0, ge=0, description="Total codes in the book")
    is_active: bool = True


class BookResponse(BaseModel):
    """Response schema for a coupon book"""
    book_id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    expiration_date: Optional[datetime]
    allow_multi_redemption: bool
    max_redemptions_per_user: int
    max_assignments_per_user: Optional[int]
    code_pattern: Optional[str]
    total_code_count: int
    is_active: bool
    
    class Config:
        from_attributes = True


class GenerateCodesRequest(BaseModel):
    """Request schema for generating coupon codes"""
    count: int = Field(..., ge=1, le=10000, description="Number of codes to generate")
    pattern: Optional[str] = Field(None, description="Pattern override (e.g., 'PROMO-{}')")
    length: int = Field(8, ge=4, le=50, description="Length of random part")
    max_redemptions: int = Field(1, ge=1, description="Max redemptions per code")


class UploadCodesRequest(BaseModel):
    """Request schema for uploading pre-generated codes"""
    codes: list[str] = Field(..., min_length=1, max_length=10000)
    max_redemptions: int = Field(1, ge=1, description="Max redemptions per code")
    
    @field_validator('codes')
    @classmethod
    def validate_codes(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Codes must be unique")
        for code in v:
            if not code or len(code) > 50:
                raise ValueError("Each code must be non-empty and <= 50 characters")
        return v


class CodeGenerationResponse(BaseModel):
    """Response schema for code generation/upload"""
    book_id: str
    codes_created: int
    codes: Optional[list[str]] = Field(None, description="Generated codes (if requested)")


# ===== Coupon Schemas =====
class CouponResponse(BaseModel):
    """Response schema for a coupon"""
    code: str
    book_id: str
    assigned_user_id: Optional[str]
    state: CouponState
    redemption_count: int
    max_redemptions: int
    is_locked: bool
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    has_redemptions_remaining: bool
    remaining_redemptions: int
    
    class Config:
        from_attributes = True
        use_enum_values = True


class AssignCouponRandomRequest(BaseModel):
    """Request schema for random coupon assignment"""
    book_id: str
    user_id: str
    count: int = Field(1, ge=1, le=100, description="Number of coupons to assign")


class AssignCouponSpecificRequest(BaseModel):
    """Request schema for specific coupon assignment"""
    user_id: str


class LockCouponRequest(BaseModel):
    """Request schema for locking a coupon"""
    user_id: str
    lock_duration_seconds: int = Field(300, ge=1, le=3600, description="Lock duration in seconds")


class RedeemCouponRequest(BaseModel):
    """Request schema for redeeming a coupon"""
    user_id: str
    metadata: Optional[dict] = Field(None, description="Order details, discount info, etc.")


class AssignmentResponse(BaseModel):
    """Response schema for coupon assignment"""
    success: bool
    assigned_count: int
    coupons: list[CouponResponse]


# ===== Redemption Schemas =====
class RedemptionHistoryResponse(BaseModel):
    """Response schema for redemption history"""
    history_id: str
    code: str
    user_id: str
    book_id: str
    redeemed_at: datetime
    redemption_metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class RedemptionResponse(BaseModel):
    """Response schema for coupon redemption"""
    success: bool
    code: str
    user_id: str
    redeemed_at: datetime
    redemption_count: int
    remaining_redemptions: int
    metadata: Optional[dict]


# ===== User Schemas (Legacy - for backward compatibility) =====
class UserCreate(BaseModel):
    """Request schema for creating a user (legacy endpoint)"""
    user_id: str
    name: str
    email: str


class UserResponse(BaseModel):
    """Response schema for a user"""
    user_id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCouponsResponse(BaseModel):
    """Response schema for user's coupons"""
    user_id: str
    total_count: int
    coupons: list[CouponResponse]


# ===== User Pool Schemas =====
class UserPoolCreate(BaseModel):
    """Schema for creating a new user pool"""
    name: str = Field(..., min_length=1, max_length=200, description="Pool name")
    description: Optional[str] = Field(None, max_length=1000, description="Pool description")
    user_ids: list[str] = Field(default_factory=list, description="Initial list of user IDs to add to pool")


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


class PoolUserInfo(BaseModel):
    """User information within a pool"""
    user_id: str
    name: str
    email: str
    added_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserPoolDetailResponse(UserPoolResponse):
    """Detailed pool response with user list"""
    users: list[PoolUserInfo] = Field(default_factory=list, description="List of users in pool")


class AddUsersToPoolRequest(BaseModel):
    """Request to add users to a pool"""
    user_ids: list[str] = Field(..., min_length=1, description="User IDs to add")


class RemoveUsersFromPoolRequest(BaseModel):
    """Request to remove users from a pool"""
    user_ids: list[str] = Field(..., min_length=1, description="User IDs to remove")


class BulkAssignCouponsRequest(BaseModel):
    """Request to bulk assign coupons from a book to a user pool"""
    book_id: str = Field(..., description="Book ID to assign coupons from")
    pool_id: str = Field(..., description="User pool ID")
    distribution_mode: str = Field(
        default="random",
        description="Distribution mode: 'random' or 'equal'"
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
    assignments: dict[str, list[str]] = Field(..., description="Map of user_id -> list of assigned codes")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
