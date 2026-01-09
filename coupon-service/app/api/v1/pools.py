"""
User Pool API routes for bulk coupon assignment
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from typing import List
import random
from datetime import datetime

from app.database import get_db
from app.models import UserPool, User, Coupon, Book
from app.schemas import (
    UserPoolCreate,
    UserPoolUpdate,
    UserPoolResponse,
    UserPoolDetailResponse,
    AddUsersToPoolRequest,
    RemoveUsersFromPoolRequest,
    BulkAssignCouponsRequest,
    BulkAssignmentResponse
)
from app.utils.auth import get_current_user
from app.utils.enums import CouponState


router = APIRouter(prefix="/api/v1/pools", tags=["User Pools"])


@router.post("/", response_model=UserPoolResponse, status_code=status.HTTP_201_CREATED)
async def create_pool(
    request: UserPoolCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user pool"""
    # Create pool
    pool = UserPool(
        name=request.name,
        description=request.description,
        created_by=current_user.user_id
    )
    
    # Add initial users if provided
    if request.user_ids:
        result = await db.execute(
            select(User).where(User.user_id.in_(request.user_ids))
        )
        users = result.scalars().all()
        pool.users = list(users)
    
    db.add(pool)
    await db.commit()
    await db.refresh(pool, ['users'])
    
    return UserPoolResponse(
        pool_id=pool.pool_id,
        name=pool.name,
        description=pool.description,
        created_by=pool.created_by,
        is_active=pool.is_active,
        created_at=pool.created_at,
        updated_at=pool.updated_at,
        user_count=len(pool.users)
    )


@router.get("/", response_model=List[UserPoolResponse])
async def list_pools(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all user pools"""
    result = await db.execute(
        select(UserPool)
        .options(selectinload(UserPool.users))
        .order_by(UserPool.created_at.desc())
    )
    pools = result.scalars().all()
    
    return [
        UserPoolResponse(
            pool_id=pool.pool_id,
            name=pool.name,
            description=pool.description,
            created_by=pool.created_by,
            is_active=pool.is_active,
            created_at=pool.created_at,
            updated_at=pool.updated_at,
            user_count=len(pool.users)
        )
        for pool in pools
    ]


@router.get("/{pool_id}", response_model=UserPoolDetailResponse)
async def get_pool(
    pool_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pool details with user list"""
    from sqlalchemy import select, text
    from app.models.user_pool import pool_users
    from app.schemas import PoolUserInfo
    
    result = await db.execute(
        select(UserPool)
        .where(UserPool.pool_id == pool_id)
        .options(selectinload(UserPool.users))
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool {pool_id} not found"
        )
    
    # Get users with added_at information from association table
    users_result = await db.execute(
        text("""
            SELECT u.user_id, u.name, u.email, pu.added_at
            FROM users u
            JOIN pool_users pu ON u.user_id = pu.user_id
            WHERE pu.pool_id = :pool_id
            ORDER BY pu.added_at DESC
        """),
        {"pool_id": pool_id}
    )
    
    users_info = [
        PoolUserInfo(
            user_id=row.user_id,
            name=row.name,
            email=row.email,
            added_at=row.added_at
        )
        for row in users_result
    ]
    
    return UserPoolDetailResponse(
        pool_id=pool.pool_id,
        name=pool.name,
        description=pool.description,
        created_by=pool.created_by,
        is_active=pool.is_active,
        created_at=pool.created_at,
        updated_at=pool.updated_at,
        user_count=len(users_info),
        users=users_info
    )


@router.patch("/{pool_id}", response_model=UserPoolResponse)
async def update_pool(
    pool_id: str,
    request: UserPoolUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update pool details"""
    result = await db.execute(
        select(UserPool)
        .where(UserPool.pool_id == pool_id)
        .options(selectinload(UserPool.users))
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool {pool_id} not found"
        )
    
    # Update fields
    if request.name is not None:
        pool.name = request.name
    if request.description is not None:
        pool.description = request.description
    if request.is_active is not None:
        pool.is_active = request.is_active
    
    await db.commit()
    await db.refresh(pool)
    
    return UserPoolResponse(
        pool_id=pool.pool_id,
        name=pool.name,
        description=pool.description,
        created_by=pool.created_by,
        is_active=pool.is_active,
        created_at=pool.created_at,
        updated_at=pool.updated_at,
        user_count=len(pool.users)
    )


@router.delete("/{pool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pool(
    pool_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a pool"""
    result = await db.execute(
        select(UserPool).where(UserPool.pool_id == pool_id)
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool {pool_id} not found"
        )
    
    await db.delete(pool)
    await db.commit()


@router.post("/{pool_id}/users", response_model=UserPoolDetailResponse)
async def add_users_to_pool(
    pool_id: str,
    request: AddUsersToPoolRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add users to a pool"""
    result = await db.execute(
        select(UserPool)
        .where(UserPool.pool_id == pool_id)
        .options(selectinload(UserPool.users))
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool {pool_id} not found"
        )
    
    # Get users to add
    result = await db.execute(
        select(User).where(User.user_id.in_(request.user_ids))
    )
    new_users = result.scalars().all()
    
    # Add users (avoiding duplicates)
    existing_user_ids = {user.user_id for user in pool.users}
    for user in new_users:
        if user.user_id not in existing_user_ids:
            pool.users.append(user)
    
    await db.commit()
    await db.refresh(pool, ['users'])
    
    return UserPoolDetailResponse(
        pool_id=pool.pool_id,
        name=pool.name,
        description=pool.description,
        created_by=pool.created_by,
        is_active=pool.is_active,
        created_at=pool.created_at,
        updated_at=pool.updated_at,
        user_count=len(pool.users),
        user_ids=[user.user_id for user in pool.users]
    )


@router.delete("/{pool_id}/users", response_model=UserPoolDetailResponse)
async def remove_users_from_pool(
    pool_id: str,
    request: RemoveUsersFromPoolRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove users from a pool"""
    result = await db.execute(
        select(UserPool)
        .where(UserPool.pool_id == pool_id)
        .options(selectinload(UserPool.users))
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool {pool_id} not found"
        )
    
    # Remove users
    pool.users = [user for user in pool.users if user.user_id not in request.user_ids]
    
    await db.commit()
    await db.refresh(pool, ['users'])
    
    return UserPoolDetailResponse(
        pool_id=pool.pool_id,
        name=pool.name,
        description=pool.description,
        created_by=pool.created_by,
        is_active=pool.is_active,
        created_at=pool.created_at,
        updated_at=pool.updated_at,
        user_count=len(pool.users),
        user_ids=[user.user_id for user in pool.users]
    )


@router.post("/bulk-assign", response_model=BulkAssignmentResponse)
async def bulk_assign_coupons(
    request: BulkAssignCouponsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk assign coupons from a book to a user pool
    
    Distribution modes:
    - 'random': Randomly distribute available coupons among pool users
    - 'equal': Distribute equal number of coupons per user (coupons_per_user)
    """
    # Get pool with users
    result = await db.execute(
        select(UserPool)
        .where(UserPool.pool_id == request.pool_id)
        .options(selectinload(UserPool.users))
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pool {request.pool_id} not found"
        )
    
    if not pool.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pool has no users"
        )
    
    # Get book
    result = await db.execute(
        select(Book).where(Book.book_id == request.book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {request.book_id} not found"
        )
    
    # Get available coupons
    result = await db.execute(
        select(Coupon)
        .where(
            Coupon.book_id == request.book_id,
            Coupon.state == CouponState.UNASSIGNED
        )
        .order_by(Coupon.code)
    )
    available_coupons = result.scalars().all()
    
    if not available_coupons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No available coupons in book {request.book_id}"
        )
    
    # Check current assignments per user if there's a limit
    user_current_assignments = {}
    if book.max_assignments_per_user is not None:
        for user in pool.users:
            result = await db.execute(
                select(func.count(Coupon.code))
                .where(
                    Coupon.book_id == request.book_id,
                    Coupon.assigned_user_id == user.user_id
                )
            )
            user_current_assignments[user.user_id] = result.scalar()
    
    # Distribute coupons
    assignments = {}
    errors = []
    total_assigned = 0
    
    if request.distribution_mode == "equal":
        # Equal distribution
        coupons_needed = len(pool.users) * request.coupons_per_user
        
        if len(available_coupons) < coupons_needed:
            errors.append(
                f"Not enough coupons: need {coupons_needed}, have {len(available_coupons)}"
            )
        
        coupon_index = 0
        for user in pool.users:
            user_coupons = []
            coupons_to_assign = request.coupons_per_user
            
            # Check max assignments limit
            if book.max_assignments_per_user is not None:
                current = user_current_assignments.get(user.user_id, 0)
                available_slots = book.max_assignments_per_user - current
                if available_slots <= 0:
                    errors.append(
                        f"User {user.user_id} has reached max assignments ({book.max_assignments_per_user})"
                    )
                    continue
                coupons_to_assign = min(coupons_to_assign, available_slots)
            
            for _ in range(coupons_to_assign):
                if coupon_index < len(available_coupons):
                    coupon = available_coupons[coupon_index]
                    coupon.state = CouponState.ASSIGNED
                    coupon.assigned_user_id = user.user_id
                    user_coupons.append(coupon.code)
                    coupon_index += 1
                    total_assigned += 1
            
            if user_coupons:
                assignments[user.user_id] = user_coupons
    
    else:  # random distribution
        # Shuffle and distribute
        random.shuffle(available_coupons)
        
        user_index = 0
        coupon_index = 0
        while coupon_index < len(available_coupons):
            user = pool.users[user_index % len(pool.users)]
            
            # Check max assignments limit
            if book.max_assignments_per_user is not None:
                current = user_current_assignments.get(user.user_id, 0) + assignments.get(user.user_id, [])
                current_count = current if isinstance(current, int) else len(current)
                if current_count >= book.max_assignments_per_user:
                    user_index += 1
                    if user_index >= len(pool.users) * 10:  # Prevent infinite loop
                        break
                    continue
            
            coupon = available_coupons[coupon_index]
            coupon.state = CouponState.ASSIGNED
            coupon.assigned_user_id = user.user_id
            
            if user.user_id not in assignments:
                assignments[user.user_id] = []
            assignments[user.user_id].append(coupon.code)
            
            total_assigned += 1
            coupon_index += 1
            user_index += 1
    
    await db.commit()
    
    return BulkAssignmentResponse(
        success=True,
        total_assigned=total_assigned,
        assignments=assignments,
        errors=errors
    )
