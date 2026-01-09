"""
Redemption service with PostgreSQL advisory lock implementation
"""
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models import Coupon, Book, RedemptionHistory
from app.utils.enums import CouponState
from app.utils.exceptions import (
    CouponNotFoundException,
    CouponLockedException,
    InvalidStateTransitionException,
    NoRedemptionsRemainingException,
    CouponExpiredException
)
from app.config import get_settings


class RedemptionService:
    """Handles coupon locking and redemption with PostgreSQL advisory locks"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def lock_coupon(
        self,
        db: AsyncSession,
        code: str,
        user_id: str,
        lock_duration_seconds: int = 300
    ) -> Coupon:
        """
        Lock a coupon using PostgreSQL advisory lock
        
        Advisory lock prevents concurrent redemption attempts on the same code.
        Lock is released automatically on session end or explicit unlock.
        
        Args:
            db: Database session
            code: Coupon code to lock
            user_id: User attempting to lock
            lock_duration_seconds: Duration in seconds
            
        Returns:
            Locked Coupon object
            
        Raises:
            CouponNotFoundException: If coupon not found
            CouponLockedException: If coupon already locked
            InvalidStateTransitionException: If state transition invalid
        """
        # Get coupon
        result = await db.execute(
            select(Coupon).where(Coupon.code == code)
        )
        coupon = result.scalar_one_or_none()
        
        if not coupon:
            raise CouponNotFoundException(f"Coupon {code} not found")
        
        # Validate state transition
        if not CouponState.is_valid_transition(coupon.state, CouponState.LOCKED):
            raise InvalidStateTransitionException(
                str(coupon.state),
                CouponState.LOCKED.value
            )
        
        # Check if already locked
        if coupon.is_locked and coupon.locked_until and coupon.locked_until > datetime.now(timezone.utc):
            raise CouponLockedException(
                f"Coupon {code} is locked until {coupon.locked_until}"
            )
        
        # Try to acquire PostgreSQL advisory lock
        # Use hashtext() to convert string to bigint for advisory lock
        lock_acquired = await self._try_acquire_advisory_lock(db, code)
        
        if not lock_acquired:
            raise CouponLockedException(
                f"Could not acquire lock on coupon {code} - concurrent access"
            )
        
        # Update coupon state
        coupon.state = CouponState.LOCKED
        coupon.is_locked = True
        coupon.locked_until = datetime.now(timezone.utc) + timedelta(seconds=lock_duration_seconds)
        
        await db.commit()
        await db.refresh(coupon)
        
        return coupon
    
    async def unlock_coupon(
        self,
        db: AsyncSession,
        code: str
    ) -> Coupon:
        """
        Unlock a coupon and release advisory lock
        
        Args:
            db: Database session
            code: Coupon code to unlock
            
        Returns:
            Unlocked Coupon object
        """
        # Get coupon
        result = await db.execute(
            select(Coupon).where(Coupon.code == code)
        )
        coupon = result.scalar_one_or_none()
        
        if not coupon:
            raise CouponNotFoundException(f"Coupon {code} not found")
        
        # Release advisory lock first and commit to ensure it's released
        await self._release_advisory_lock(db, code)
        await db.commit()  # Commit the lock release immediately
        
        # Revert to previous state (ASSIGNED if has user, otherwise UNASSIGNED)
        if coupon.assigned_user_id:
            coupon.state = CouponState.ASSIGNED
        else:
            coupon.state = CouponState.UNASSIGNED
        
        coupon.is_locked = False
        coupon.locked_until = None
        
        await db.commit()
        await db.refresh(coupon)
        
        return coupon
    
    async def redeem_coupon(
        self,
        db: AsyncSession,
        code: str,
        user_id: str,
        metadata: Optional[dict] = None
    ) -> tuple[Coupon, RedemptionHistory]:
        """
        Redeem a coupon with advisory lock protection
        
        Handles both single and multi-redemption coupons.
        Creates audit trail in RedemptionHistory.
        
        Args:
            db: Database session
            code: Coupon code to redeem
            user_id: User redeeming the coupon
            metadata: Optional metadata (order info, etc.)
            
        Returns:
            Tuple of (Coupon, RedemptionHistory)
            
        Raises:
            CouponNotFoundException: If coupon not found
            CouponExpiredException: If coupon expired
            NoRedemptionsRemainingException: If no redemptions left
            CouponLockedException: If cannot acquire lock
        """
        # Try to acquire advisory lock
        lock_acquired = await self._try_acquire_advisory_lock(db, code)
        if not lock_acquired:
            raise CouponLockedException(
                f"Could not acquire lock on coupon {code} - concurrent redemption"
            )
        
        try:
            # Get coupon with row lock
            result = await db.execute(
                select(Coupon)
                .where(Coupon.code == code)
                .with_for_update()
            )
            coupon = result.scalar_one_or_none()
            
            if not coupon:
                raise CouponNotFoundException(f"Coupon {code} not found")
            
            # Get book to check expiration and config
            result = await db.execute(
                select(Book).where(Book.book_id == coupon.book_id)
            )
            book = result.scalar_one()
            
            # Check expiration
            if book.expiration_date and book.expiration_date < datetime.now(timezone.utc):
                coupon.state = CouponState.EXPIRED
                await db.commit()
                raise CouponExpiredException(f"Coupon {code} has expired")
            
            # Check if redemptions remaining
            if not coupon.has_redemptions_remaining:
                raise NoRedemptionsRemainingException(
                    f"Coupon {code} has no remaining redemptions "
                    f"({coupon.redemption_count}/{coupon.max_redemptions})"
                )
            
            # Validate state (must be ASSIGNED, or already REDEEMED for multi-use)
            # LOCKED coupons cannot be redeemed - must unlock first
            valid_states = [CouponState.ASSIGNED]
            if book.allow_multi_redemption:
                valid_states.append(CouponState.REDEEMED)
            
            if coupon.state not in valid_states:
                # Special message for LOCKED state
                if coupon.state == CouponState.LOCKED:
                    raise InvalidStateTransitionException(
                        str(coupon.state),
                        "REDEEMED - Unlock the coupon first"
                    )
                else:
                    raise InvalidStateTransitionException(
                        str(coupon.state),
                        "REDEEMED"
                    )
            
            # Check max redemptions per user (if book has this limit)
            if book.max_redemptions_per_user:
                result = await db.execute(
                    select(RedemptionHistory)
                    .where(
                        RedemptionHistory.code == code,
                        RedemptionHistory.user_id == user_id
                    )
                )
                user_redemptions = len(result.scalars().all())
                
                if user_redemptions >= book.max_redemptions_per_user:
                    raise NoRedemptionsRemainingException(
                        f"User {user_id} has reached max redemptions "
                        f"({book.max_redemptions_per_user}) for this coupon"
                    )
            
            # Perform redemption
            coupon.redemption_count += 1
            
            # Update state based on remaining redemptions
            if coupon.has_redemptions_remaining:
                coupon.state = CouponState.REDEEMED  # Still can be redeemed
            else:
                coupon.state = CouponState.REDEEMED  # Fully redeemed
            
            # Clear lock
            coupon.is_locked = False
            coupon.locked_until = None
            
            # Create redemption history record
            history = RedemptionHistory(
                code=code,
                user_id=user_id,
                book_id=coupon.book_id,
                redemption_metadata=metadata
            )
            db.add(history)
            
            await db.commit()
            await db.refresh(coupon)
            await db.refresh(history)
            
            return coupon, history
            
        finally:
            # Always release advisory lock
            await self._release_advisory_lock(db, code)
    
    async def _try_acquire_advisory_lock(self, db: AsyncSession, code: str) -> bool:
        """
        Try to acquire PostgreSQL advisory lock on a coupon code
        
        Uses hashtext() to convert string to bigint for pg_try_advisory_lock()
        
        Args:
            db: Database session
            code: Coupon code
            
        Returns:
            True if lock acquired, False otherwise
        """
        result = await db.execute(
            text("SELECT pg_try_advisory_lock(hashtext(:code))"),
            {"code": code}
        )
        lock_acquired = result.scalar()
        return bool(lock_acquired)
    
    async def _release_advisory_lock(self, db: AsyncSession, code: str):
        """
        Release PostgreSQL advisory lock on a coupon code
        
        Args:
            db: Database session
            code: Coupon code
        """
        await db.execute(
            text("SELECT pg_advisory_unlock(hashtext(:code))"),
            {"code": code}
        )
