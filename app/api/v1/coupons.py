"""
Coupon assignment and management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Coupon
from app.schemas import (
    AssignCouponRandomRequest,
    AssignCouponSpecificRequest,
    LockCouponRequest,
    RedeemCouponRequest,
    AssignmentResponse,
    CouponResponse,
    RedemptionResponse
)
from app.services.assignment_service import AssignmentService
from app.services.redemption_service import RedemptionService
from app.utils.exceptions import (
    CouponNotFoundException,
    CouponLockedException,
    NoCodesAvailableException,
    MaxAssignmentsReachedException,
    InvalidStateTransitionException,
    NoRedemptionsRemainingException,
    CouponExpiredException
)


router = APIRouter(prefix="/api/v1/coupons", tags=["Coupons"])


@router.post("/assign", response_model=AssignmentResponse)
async def assign_random_coupons(
    request: AssignCouponRandomRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Randomly assign coupons from a book to a user
    
    Uses ORDER BY RANDOM() for true randomness
    """
    assignment_service = AssignmentService()
    
    try:
        coupons = await assignment_service.assign_random_coupons(
            db=db,
            book_id=request.book_id,
            user_id=request.user_id,
            count=request.count
        )
        
        return AssignmentResponse(
            success=True,
            assigned_count=len(coupons),
            coupons=[CouponResponse.model_validate(c) for c in coupons]
        )
        
    except NoCodesAvailableException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MaxAssignmentsReachedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except CouponNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/assign/{code}", response_model=CouponResponse)
async def assign_specific_coupon(
    code: str,
    request: AssignCouponSpecificRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Assign a specific coupon code to a user
    """
    assignment_service = AssignmentService()
    
    try:
        coupon = await assignment_service.assign_specific_coupon(
            db=db,
            code=code,
            user_id=request.user_id
        )
        
        return CouponResponse.model_validate(coupon)
        
    except CouponNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MaxAssignmentsReachedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/lock/{code}", response_model=CouponResponse)
async def lock_coupon(
    code: str,
    request: LockCouponRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Lock a coupon for redemption using PostgreSQL advisory lock
    
    Lock prevents concurrent redemption and expires after specified duration
    """
    redemption_service = RedemptionService()
    
    try:
        coupon = await redemption_service.lock_coupon(
            db=db,
            code=code,
            user_id=request.user_id,
            lock_duration_seconds=request.lock_duration_seconds
        )
        
        return CouponResponse.model_validate(coupon)
        
    except CouponNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CouponLockedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except InvalidStateTransitionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/unlock/{code}", response_model=CouponResponse)
async def unlock_coupon(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Unlock a coupon and release advisory lock
    """
    redemption_service = RedemptionService()
    
    try:
        coupon = await redemption_service.unlock_coupon(db=db, code=code)
        return CouponResponse.model_validate(coupon)
        
    except CouponNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/redeem/{code}", response_model=RedemptionResponse)
async def redeem_coupon(
    code: str,
    request: RedeemCouponRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Redeem a coupon with advisory lock protection
    
    Handles both single and multi-redemption coupons.
    Creates audit trail in RedemptionHistory.
    """
    redemption_service = RedemptionService()
    
    try:
        coupon, history = await redemption_service.redeem_coupon(
            db=db,
            code=code,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        return RedemptionResponse(
            success=True,
            code=coupon.code,
            user_id=request.user_id,
            redeemed_at=history.redeemed_at,
            redemption_count=coupon.redemption_count,
            remaining_redemptions=coupon.remaining_redemptions,
            metadata=history.redemption_metadata
        )
        
    except CouponNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CouponLockedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (InvalidStateTransitionException, NoRedemptionsRemainingException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CouponExpiredException as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(e)
        )


@router.get("/{code}", response_model=CouponResponse)
async def get_coupon(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get coupon details by code"""
    result = await db.execute(
        select(Coupon).where(Coupon.code == code)
    )
    coupon = result.scalar_one_or_none()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coupon {code} not found"
        )
    
    return CouponResponse.model_validate(coupon)
