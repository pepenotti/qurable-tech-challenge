"""
Assignment service for randomly assigning coupons to users
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models import Coupon, Book
from app.utils.enums import CouponState
from app.utils.exceptions import (
    NoCodesAvailableException,
    MaxAssignmentsReachedException,
    CouponNotFoundException
)


class AssignmentService:
    """Handles coupon assignment logic"""
    
    @staticmethod
    async def assign_random_coupons(
        db: AsyncSession,
        book_id: str,
        user_id: str,
        count: int
    ) -> List[Coupon]:
        """
        Randomly assign available coupons to a user
        
        Uses ORDER BY RANDOM() for true randomness with LIMIT for performance
        
        Args:
            db: Database session
            book_id: Book ID to assign from
            user_id: User ID to assign to
            count: Number of coupons to assign
            
        Returns:
            List of assigned Coupon objects
            
        Raises:
            NoCodesAvailableException: If not enough unassigned coupons
            MaxAssignmentsReachedException: If user exceeded assignment limit
        """
        # Check book exists and get configuration
        result = await db.execute(
            select(Book).where(Book.book_id == book_id)
        )
        book = result.scalar_one_or_none()
        if not book:
            raise CouponNotFoundException(f"Book {book_id} not found")
        
        # Check max assignments per user limit
        if book.max_assignments_per_user is not None:
            result = await db.execute(
                select(func.count(Coupon.code))
                .where(
                    and_(
                        Coupon.book_id == book_id,
                        Coupon.assigned_user_id == user_id
                    )
                )
            )
            current_assignments = result.scalar()
            
            if current_assignments + count > book.max_assignments_per_user:
                raise MaxAssignmentsReachedException(
                    f"User {user_id} can only have {book.max_assignments_per_user} "
                    f"assignments from this book. Current: {current_assignments}, "
                    f"Requested: {count}"
                )
        
        # Find available unassigned coupons (ORDER BY RANDOM() with LIMIT)
        result = await db.execute(
            select(Coupon)
            .where(
                and_(
                    Coupon.book_id == book_id,
                    Coupon.state == CouponState.UNASSIGNED
                )
            )
            .order_by(func.random())
            .limit(count)
            .with_for_update(skip_locked=True)  # Skip locked rows for concurrency
        )
        available_coupons = result.scalars().all()
        
        if len(available_coupons) < count:
            raise NoCodesAvailableException(
                f"Not enough unassigned coupons. Requested: {count}, "
                f"Available: {len(available_coupons)}"
            )
        
        # Assign coupons to user
        assigned_coupons = []
        for coupon in available_coupons:
            coupon.assigned_user_id = user_id
            coupon.state = CouponState.ASSIGNED
            assigned_coupons.append(coupon)
        
        await db.commit()
        
        # Refresh to get updated relationships
        for coupon in assigned_coupons:
            await db.refresh(coupon)
        
        return assigned_coupons
    
    @staticmethod
    async def assign_specific_coupon(
        db: AsyncSession,
        code: str,
        user_id: str
    ) -> Coupon:
        """
        Assign a specific coupon code to a user
        
        Args:
            db: Database session
            code: Coupon code to assign
            user_id: User ID to assign to
            
        Returns:
            Assigned Coupon object
            
        Raises:
            CouponNotFoundException: If coupon not found or not available
            MaxAssignmentsReachedException: If user exceeded assignment limit
        """
        # Get coupon with lock
        result = await db.execute(
            select(Coupon)
            .where(Coupon.code == code)
            .with_for_update(skip_locked=False)
        )
        coupon = result.scalar_one_or_none()
        
        if not coupon:
            raise CouponNotFoundException(f"Coupon {code} not found")
        
        if coupon.state != CouponState.UNASSIGNED:
            raise CouponNotFoundException(
                f"Coupon {code} is not available for assignment (state: {coupon.state})"
            )
        
        # Check max assignments per user limit
        result = await db.execute(select(Book).where(Book.book_id == coupon.book_id))
        book = result.scalar_one()
        
        if book.max_assignments_per_user is not None:
            result = await db.execute(
                select(func.count(Coupon.code))
                .where(
                    and_(
                        Coupon.book_id == coupon.book_id,
                        Coupon.assigned_user_id == user_id
                    )
                )
            )
            current_assignments = result.scalar()
            
            if current_assignments + 1 > book.max_assignments_per_user:
                raise MaxAssignmentsReachedException(
                    f"User {user_id} has reached maximum assignments "
                    f"({book.max_assignments_per_user}) for this book"
                )
        
        # Assign coupon
        coupon.assigned_user_id = user_id
        coupon.state = CouponState.ASSIGNED
        
        await db.commit()
        await db.refresh(coupon)
        
        return coupon
