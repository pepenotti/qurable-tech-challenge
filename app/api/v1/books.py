"""
Book management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import Book, Coupon, RedemptionHistory
from app.schemas import (
    CreateBookRequest,
    BookResponse,
    GenerateCodesRequest,
    UploadCodesRequest,
    CodeGenerationResponse,
    CouponResponse,
    RedemptionHistoryResponse
)
from app.services.code_generator import CodeGenerator
from app.utils.exceptions import DuplicateCodeException


router = APIRouter(prefix="/api/v1/books", tags=["Books"])


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    request: CreateBookRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new coupon book"""
    # Validate pattern if provided
    if request.code_pattern:
        generator = CodeGenerator()
        if not generator.validate_pattern(request.code_pattern):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid code pattern. Use alphanumeric, dash, underscore, and {} placeholder"
            )
    
    # Create book
    book = Book(
        name=request.name,
        description=request.description,
        owner_id=request.owner_id,
        expiration_date=request.expiration_date,
        allow_multi_redemption=request.allow_multi_redemption,
        max_redemptions_per_user=request.max_redemptions_per_user,
        max_assignments_per_user=request.max_assignments_per_user,
        code_pattern=request.code_pattern,
        total_code_count=request.total_code_count,
        is_active=request.is_active
    )
    
    db.add(book)
    await db.commit()
    await db.refresh(book)
    
    return book


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a coupon book by ID"""
    result = await db.execute(
        select(Book).where(Book.book_id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )
    
    return book


@router.get("/", response_model=List[BookResponse])
async def list_books(
    owner_id: str = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List coupon books with optional filters"""
    query = select(Book)
    
    if owner_id:
        query = query.where(Book.owner_id == owner_id)
    if is_active is not None:
        query = query.where(Book.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    books = result.scalars().all()
    
    return books


@router.post("/{book_id}/codes/generate", response_model=CodeGenerationResponse)
async def generate_codes(
    book_id: str,
    request: GenerateCodesRequest,
    include_codes: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate random coupon codes for a book
    
    Args:
        book_id: Book ID
        request: Generation parameters
        include_codes: Whether to return generated codes in response (default: False for large batches)
    """
    # Get book
    result = await db.execute(
        select(Book).where(Book.book_id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )
    
    # Get existing codes for this book to avoid collisions
    result = await db.execute(
        select(Coupon.code).where(Coupon.book_id == book_id)
    )
    existing_codes = set(result.scalars().all())
    
    # Generate codes
    generator = CodeGenerator()
    pattern = request.pattern or book.code_pattern
    
    try:
        codes = generator.generate_codes(
            count=request.count,
            pattern=pattern,
            length=request.length,
            existing_codes=existing_codes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create coupon records
    coupons = [
        Coupon(
            code=code,
            book_id=book_id,
            max_redemptions=request.max_redemptions
        )
        for code in codes
    ]
    
    db.add_all(coupons)
    
    # Update book total count
    book.total_code_count += len(codes)
    
    await db.commit()
    
    return CodeGenerationResponse(
        book_id=book_id,
        codes_created=len(codes),
        codes=codes if include_codes else None
    )


@router.post("/{book_id}/codes/upload", response_model=CodeGenerationResponse)
async def upload_codes(
    book_id: str,
    request: UploadCodesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload pre-generated coupon codes for a book
    
    Args:
        book_id: Book ID
        request: List of codes to upload
    """
    # Get book
    result = await db.execute(
        select(Book).where(Book.book_id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )
    
    # Check for duplicate codes in database
    result = await db.execute(
        select(Coupon.code).where(Coupon.code.in_(request.codes))
    )
    existing = result.scalars().all()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Codes already exist: {', '.join(existing[:5])}..."
        )
    
    # Create coupon records
    coupons = [
        Coupon(
            code=code,
            book_id=book_id,
            max_redemptions=request.max_redemptions
        )
        for code in request.codes
    ]
    
    db.add_all(coupons)
    
    # Update book total count
    book.total_code_count += len(request.codes)
    
    await db.commit()
    
    return CodeGenerationResponse(
        book_id=book_id,
        codes_created=len(request.codes),
        codes=None
    )


@router.get("/{book_id}/coupons", response_model=List[CouponResponse])
async def get_book_coupons(
    book_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all coupons for a specific book
    
    Args:
        book_id: Book ID
        skip: Pagination offset
        limit: Pagination limit
    """
    # Check if book exists
    result = await db.execute(
        select(Book).where(Book.book_id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )
    
    # Get coupons
    query = select(Coupon).where(Coupon.book_id == book_id).offset(skip).limit(limit)
    result = await db.execute(query)
    coupons = result.scalars().all()
    
    return [CouponResponse.model_validate(c) for c in coupons]


@router.get("/{book_id}/redemption-history", response_model=List[RedemptionHistoryResponse])
async def get_book_redemption_history(
    book_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get redemption history for a specific book
    
    Args:
        book_id: Book ID
        skip: Pagination offset
        limit: Pagination limit
    """
    # Check if book exists
    result = await db.execute(
        select(Book).where(Book.book_id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )
    
    # Get redemption history
    query = (
        select(RedemptionHistory)
        .where(RedemptionHistory.book_id == book_id)
        .order_by(RedemptionHistory.redeemed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    history = result.scalars().all()
    
    return [RedemptionHistoryResponse.model_validate(h) for h in history]
