"""
Database initialization script
Creates all tables and optionally creates an admin user
"""
import asyncio
import sys
from app.database import engine, Base
from app.models import User, Book, Coupon, UserPool
from app.models.user import UserRole
from app.utils.auth import get_password_hash
from sqlalchemy import text


async def drop_all_tables():
    """Drop all tables"""
    print("🗑️  Dropping all tables...")
    async with engine.begin() as conn:
        # Drop tables in correct order (respect foreign keys)
        await conn.execute(text("DROP TABLE IF EXISTS pool_users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS user_pools CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS coupons CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS books CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS couponstate CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
    print("✅ All tables dropped")


async def create_all_tables():
    """Create all tables from models"""
    print("🔨 Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created")


async def create_admin_user(email: str, password: str, name: str = "Admin User"):
    """Create an admin user"""
    print(f"👤 Creating admin user: {email}")
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"⚠️  User {email} already exists, skipping...")
            return existing_user
        
        # Create new admin user
        admin = User(
            email=email,
            name=name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        print(f"✅ Admin user created: {admin.email} (ID: {admin.user_id})")
        return admin


async def create_mock_users():
    """Create mock regular users for demo"""
    print("\n👥 Creating mock users...")
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    
    mock_users_data = [
        {"email": "alice@example.com", "name": "Alice Johnson", "password": "demo123"},
        {"email": "bob@example.com", "name": "Bob Smith", "password": "demo123"},
        {"email": "charlie@example.com", "name": "Charlie Brown", "password": "demo123"},
        {"email": "diana@example.com", "name": "Diana Prince", "password": "demo123"},
        {"email": "eve@example.com", "name": "Eve Davis", "password": "demo123"},
    ]
    
    created_users = []
    async with AsyncSessionLocal() as session:
        for user_data in mock_users_data:
            # Check if exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                user = User(
                    email=user_data["email"],
                    name=user_data["name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=UserRole.USER,
                    is_active=True
                )
                session.add(user)
                created_users.append(user)
            else:
                created_users.append(existing)
        
        await session.commit()
        for user in created_users:
            await session.refresh(user)
    
    print(f"✅ Created {len(created_users)} mock users")
    return created_users


async def create_mock_books(admin_user):
    """Create mock coupon books"""
    print("\n📚 Creating mock coupon books...")
    from app.database import AsyncSessionLocal
    from datetime import datetime, timedelta
    
    books_data = [
        {
            "name": "Summer Sale 2026",
            "description": "20% discount on all summer items",
            "code_count": 50,
            "code_pattern": "SUMMER-{}-2026"
        },
        {
            "name": "VIP Access Codes",
            "description": "Exclusive VIP member access codes",
            "code_count": 20,
            "code_pattern": "VIP-{}"
        },
        {
            "name": "Free Shipping Vouchers",
            "description": "Free shipping on orders over $50",
            "code_count": 100,
            "code_pattern": "SHIP-{}"
        },
        {
            "name": "Beta Tester Rewards",
            "description": "Thank you codes for beta testers",
            "code_count": 30,
            "code_pattern": "BETA-{}-THANKS"
        },
    ]
    
    created_books = []
    async with AsyncSessionLocal() as session:
        for book_data in books_data:
            from app.models.book import Book
            import uuid
            
            book = Book(
                book_id=str(uuid.uuid4()),
                name=book_data["name"],
                description=book_data["description"],
                owner_id=admin_user.user_id,
                expiration_date=datetime.utcnow() + timedelta(days=90),
                allow_multi_redemption=False,
                max_redemptions_per_user=1,
                max_assignments_per_user=2,
                code_pattern=book_data["code_pattern"],
                total_code_count=book_data["code_count"],
                is_active=True
            )
            session.add(book)
            created_books.append(book)
        
        await session.commit()
        for book in created_books:
            await session.refresh(book)
    
    print(f"✅ Created {len(created_books)} coupon books")
    return created_books


async def create_mock_coupons(books):
    """Create mock coupons for each book"""
    print("\n🎟️  Creating mock coupons...")
    from app.database import AsyncSessionLocal
    from app.models.coupon import Coupon
    import random
    import string
    
    total_coupons = 0
    async with AsyncSessionLocal() as session:
        for book in books:
            # Generate random codes for each book
            for i in range(book.total_code_count):
                # Generate random code part
                random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                # Apply pattern if exists
                if book.code_pattern and '{}' in book.code_pattern:
                    code = book.code_pattern.replace('{}', random_part)
                else:
                    code = random_part
                
                coupon = Coupon(
                    code=code,
                    book_id=book.book_id,
                    assigned_user_id=None,
                    state="UNASSIGNED",
                    redemption_count=0,
                    max_redemptions=book.max_redemptions_per_user,
                    is_locked=False,
                    locked_until=None
                )
                session.add(coupon)
                total_coupons += 1
        
        await session.commit()
    
    print(f"✅ Created {total_coupons} coupons across all books")
    return total_coupons


async def create_mock_pools(admin_user, mock_users):
    """Create mock user pools"""
    print("\n🏊 Creating mock user pools...")
    from app.database import AsyncSessionLocal
    from app.models.user_pool import UserPool
    from sqlalchemy import text
    import uuid
    import random
    
    pools_data = [
        {
            "name": "Beta Testers",
            "description": "Early access beta testing group",
            "user_count": 3
        },
        {
            "name": "VIP Members",
            "description": "Premium VIP membership tier",
            "user_count": 2
        },
        {
            "name": "Marketing Campaign Q1",
            "description": "Users from Q1 2026 marketing campaign",
            "user_count": 4
        },
    ]
    
    created_pools = []
    async with AsyncSessionLocal() as session:
        for pool_data in pools_data:
            pool_id = str(uuid.uuid4())
            pool = UserPool(
                pool_id=pool_id,
                name=pool_data["name"],
                description=pool_data["description"],
                created_by=admin_user.user_id,
                is_active=True
            )
            session.add(pool)
            await session.flush()
            
            # Add random users to pool via raw SQL
            selected_users = random.sample(mock_users, min(pool_data["user_count"], len(mock_users)))
            for user in selected_users:
                await session.execute(
                    text("INSERT INTO pool_users (pool_id, user_id) VALUES (:pool_id, :user_id)"),
                    {"pool_id": pool_id, "user_id": user.user_id}
                )
            
            created_pools.append(pool)
        
        await session.commit()
    
    print(f"✅ Created {len(created_pools)} user pools with assigned users")
    return created_pools


async def assign_some_coupons(books, mock_users):
    """Assign some coupons to users and redeem a few"""
    print("\n🎁 Assigning and redeeming some coupons...")
    from app.database import AsyncSessionLocal
    from sqlalchemy import select
    from app.models.coupon import Coupon
    import random
    
    async with AsyncSessionLocal() as session:
        # Get some unassigned coupons from each book
        assigned_count = 0
        redeemed_count = 0
        
        for book in books[:2]:  # Only first 2 books
            result = await session.execute(
                select(Coupon)
                .where(Coupon.book_id == book.book_id)
                .where(Coupon.state == "UNASSIGNED")
                .limit(10)
            )
            coupons = result.scalars().all()
            
            # Assign to random users
            for coupon in coupons[:5]:
                user = random.choice(mock_users)
                coupon.assigned_user_id = user.user_id
                coupon.state = "ASSIGNED"
                assigned_count += 1
            
            # Redeem a couple
            for coupon in coupons[5:7]:
                user = random.choice(mock_users)
                coupon.assigned_user_id = user.user_id
                coupon.state = "REDEEMED"
                coupon.redemption_count = 1
                redeemed_count += 1
        
        await session.commit()
    
    print(f"✅ Assigned {assigned_count} coupons, redeemed {redeemed_count} coupons")
    return assigned_count, redeemed_count


async def init_database(drop_existing: bool = False, create_admin: bool = True, with_mock_data: bool = False):
    """Initialize the database"""
    print("\n" + "="*60)
    print("🚀 Database Initialization")
    print("="*60 + "\n")
    
    try:
        if drop_existing:
            await drop_all_tables()
        
        await create_all_tables()
        
        admin_user = None
        if create_admin:
            admin_email = "admin@example.com"
            admin_password = "admin123"
            admin_name = "Admin User"
            
            admin_user = await create_admin_user(admin_email, admin_password, admin_name)
            print(f"\n📝 Admin credentials:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
        
        if with_mock_data and admin_user:
            print("\n" + "="*60)
            print("🎭 Creating Mock Data for Showcase")
            print("="*60)
            
            # Create mock users
            mock_users = await create_mock_users()
            print(f"   👥 Users: {len(mock_users)} regular users")
            print(f"   📧 All user passwords: demo123")
            
            # Create books
            books = await create_mock_books(admin_user)
            print(f"   📚 Books: {len(books)} coupon books")
            
            # Create coupons
            coupon_count = await create_mock_coupons(books)
            print(f"   🎟️  Coupons: {coupon_count} total coupons")
            
            # Create pools
            pools = await create_mock_pools(admin_user, mock_users)
            print(f"   🏊 Pools: {len(pools)} user pools")
            
            # Assign and redeem some coupons
            assigned, redeemed = await assign_some_coupons(books, mock_users)
            print(f"   🎁 Activity: {assigned} assigned, {redeemed} redeemed")
            
            print("\n" + "="*60)
            print("✅ Mock data created successfully!")
            print("="*60)
        
        print("\n" + "="*60)
        print("✅ Database initialization complete!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all existing tables before creating new ones"
    )
    parser.add_argument(
        "--no-admin",
        action="store_true",
        help="Don't create an admin user"
    )
    parser.add_argument(
        "--with-mock-data",
        action="store_true",
        help="Create mock data for showcase (users, books, coupons, pools)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(init_database(
        drop_existing=args.drop,
        create_admin=not args.no_admin,
        with_mock_data=args.with_mock_data
    ))
