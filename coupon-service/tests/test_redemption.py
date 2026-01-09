"""
Tests for coupon redemption service
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book, Coupon, User, RedemptionHistory
from app.services.redemption_service import RedemptionService
from app.utils.enums import CouponState
from app.utils.exceptions import (
    CouponNotFoundException,
    CouponLockedException,
    NoRedemptionsRemainingException,
    CouponExpiredException
)


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user"""
    user = User(
        user_id="user-123",
        name="Test User",
        email="test@example.com"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_book(db: AsyncSession, test_user):
    """Create a test book"""
    book = Book(
        book_id="book-123",
        name="Test Book",
        owner_id=test_user.user_id,
        allow_multi_redemption=False,
        max_redemptions_per_user=1,
        is_active=True
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


@pytest.fixture
async def test_coupon(db: AsyncSession, test_book, test_user):
    """Create a test coupon"""
    coupon = Coupon(
        code="TEST-COUPON-001",
        book_id=test_book.book_id,
        assigned_user_id=test_user.user_id,
        state=CouponState.ASSIGNED,
        max_redemptions=1
    )
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return coupon


@pytest.mark.asyncio
async def test_lock_coupon(db: AsyncSession, test_coupon, test_user):
    """Test locking a coupon"""
    service = RedemptionService()
    
    locked_coupon = await service.lock_coupon(
        db=db,
        code=test_coupon.code,
        user_id=test_user.user_id,
        lock_duration_seconds=300
    )
    
    assert locked_coupon.state == CouponState.LOCKED
    assert locked_coupon.is_locked is True
    assert locked_coupon.locked_until is not None
    assert locked_coupon.locked_until > datetime.utcnow()


@pytest.mark.asyncio
async def test_unlock_coupon(db: AsyncSession, test_coupon, test_user):
    """Test unlocking a coupon"""
    service = RedemptionService()
    
    # First lock
    await service.lock_coupon(
        db=db,
        code=test_coupon.code,
        user_id=test_user.user_id
    )
    
    # Then unlock
    unlocked_coupon = await service.unlock_coupon(db=db, code=test_coupon.code)
    
    assert unlocked_coupon.state == CouponState.ASSIGNED
    assert unlocked_coupon.is_locked is False
    assert unlocked_coupon.locked_until is None


@pytest.mark.asyncio
async def test_redeem_coupon_success(db: AsyncSession, test_coupon, test_user):
    """Test successful coupon redemption"""
    service = RedemptionService()
    
    coupon, history = await service.redeem_coupon(
        db=db,
        code=test_coupon.code,
        user_id=test_user.user_id,
        metadata={"order_id": "ORDER-123"}
    )
    
    assert coupon.state == CouponState.REDEEMED
    assert coupon.redemption_count == 1
    assert coupon.has_redemptions_remaining is False
    assert history.code == test_coupon.code
    assert history.user_id == test_user.user_id
    assert history.redemption_metadata["order_id"] == "ORDER-123"


@pytest.mark.asyncio
async def test_redeem_coupon_no_redemptions_remaining(
    db: AsyncSession, 
    test_coupon, 
    test_user
):
    """Test redemption fails when no redemptions remaining"""
    service = RedemptionService()
    
    # First redemption
    await service.redeem_coupon(
        db=db,
        code=test_coupon.code,
        user_id=test_user.user_id
    )
    
    # Second redemption should fail
    with pytest.raises(NoRedemptionsRemainingException):
        await service.redeem_coupon(
            db=db,
            code=test_coupon.code,
            user_id=test_user.user_id
        )


@pytest.mark.asyncio
async def test_multi_redemption_coupon(db: AsyncSession, test_book, test_user):
    """Test multi-redemption coupon"""
    # Update book to allow multi-redemption
    test_book.allow_multi_redemption = True
    test_book.max_redemptions_per_user = 3
    await db.commit()
    
    # Create multi-redemption coupon
    coupon = Coupon(
        code="MULTI-REDEMPTION-001",
        book_id=test_book.book_id,
        assigned_user_id=test_user.user_id,
        state=CouponState.ASSIGNED,
        max_redemptions=3
    )
    db.add(coupon)
    await db.commit()
    
    service = RedemptionService()
    
    # First redemption
    coupon1, _ = await service.redeem_coupon(
        db=db,
        code=coupon.code,
        user_id=test_user.user_id
    )
    assert coupon1.redemption_count == 1
    assert coupon1.has_redemptions_remaining is True
    
    # Second redemption
    coupon2, _ = await service.redeem_coupon(
        db=db,
        code=coupon.code,
        user_id=test_user.user_id
    )
    assert coupon2.redemption_count == 2
    assert coupon2.has_redemptions_remaining is True
    
    # Third redemption
    coupon3, _ = await service.redeem_coupon(
        db=db,
        code=coupon.code,
        user_id=test_user.user_id
    )
    assert coupon3.redemption_count == 3
    assert coupon3.has_redemptions_remaining is False


@pytest.mark.asyncio
async def test_expired_coupon_redemption(db: AsyncSession, test_book, test_user):
    """Test redemption fails for expired coupon"""
    # Set book expiration in the past
    test_book.expiration_date = datetime.utcnow() - timedelta(days=1)
    await db.commit()
    
    coupon = Coupon(
        code="EXPIRED-001",
        book_id=test_book.book_id,
        assigned_user_id=test_user.user_id,
        state=CouponState.ASSIGNED
    )
    db.add(coupon)
    await db.commit()
    
    service = RedemptionService()
    
    with pytest.raises(CouponExpiredException):
        await service.redeem_coupon(
            db=db,
            code=coupon.code,
            user_id=test_user.user_id
        )
