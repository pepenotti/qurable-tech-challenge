from fastapi import HTTPException, status


class CouponServiceException(HTTPException):
    """Base exception for coupon service"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class CouponNotFoundException(CouponServiceException):
    """Coupon not found"""
    def __init__(self, code: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coupon with code '{code}' not found"
        )


class BookNotFoundException(CouponServiceException):
    """Book not found"""
    def __init__(self, book_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID '{book_id}' not found"
        )


class CouponAlreadyAssignedException(CouponServiceException):
    """Coupon already assigned"""
    def __init__(self, code: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coupon '{code}' is already assigned"
        )


class CouponLockedException(CouponServiceException):
    """Coupon is currently locked"""
    def __init__(self, code: str, retry_after: int = 5):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Coupon '{code}' is currently locked. Try again in {retry_after} seconds"
        )


class InvalidStateTransitionException(CouponServiceException):
    """Invalid state transition"""
    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition from '{from_state}' to '{to_state}'"
        )


class MaxAssignmentsReachedException(CouponServiceException):
    """User reached max assignments for this book"""
    def __init__(self, limit: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum assignments limit ({limit}) reached for this book"
        )


class NoRedemptionsRemainingException(CouponServiceException):
    """No redemptions remaining"""
    def __init__(self, code: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coupon '{code}' has no redemptions remaining"
        )


class NoCodesAvailableException(CouponServiceException):
    """No unassigned codes available"""
    def __init__(self, book_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No unassigned codes available in book '{book_id}'"
        )


class CouponExpiredException(CouponServiceException):
    """Coupon has expired"""
    def __init__(self, code: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coupon '{code}' has expired"
        )


class DuplicateCodeException(CouponServiceException):
    """Duplicate code detected"""
    def __init__(self, code: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Code '{code}' already exists"
        )
