"""
User-related API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Coupon
from app.schemas import UserCreate, UserResponse, UserCouponsResponse, CouponResponse


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.user_id == user_data.user_id)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_data.user_id} already exists"
        )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_email = result.scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {user_data.email} already in use"
        )
    
    # Create new user
    new_user = User(
        user_id=user_data.user_id,
        name=user_data.name,
        email=user_data.email
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.get("/search/by-email", response_model=UserResponse)
async def search_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Search for a user by email address"""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user details by ID"""
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user


@router.get("/{user_id}/coupons", response_model=UserCouponsResponse)
async def get_user_coupons(
    user_id: str,
    book_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all coupons assigned to a user
    
    Args:
        user_id: User ID
        book_id: Optional filter by book ID
        skip: Pagination offset
        limit: Pagination limit
    """
    query = select(Coupon).where(Coupon.assigned_user_id == user_id)
    
    if book_id:
        query = query.where(Coupon.book_id == book_id)
    
    # Get total count
    count_query = select(Coupon).where(Coupon.assigned_user_id == user_id)
    if book_id:
        count_query = count_query.where(Coupon.book_id == book_id)
    
    result = await db.execute(count_query)
    total_count = len(result.scalars().all())
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    coupons = result.scalars().all()
    
    return UserCouponsResponse(
        user_id=user_id,
        total_count=total_count,
        coupons=[CouponResponse.model_validate(c) for c in coupons]
    )
