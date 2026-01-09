# Coupon Book Service - FastAPI Application

A RESTful API service for managing coupon books, codes, assignments, and redemptions.

## Features

- ✅ Create and manage coupon books
- ✅ Generate or upload coupon codes
- ✅ Random coupon assignment with fairness
- ✅ PostgreSQL advisory locks for concurrency control
- ✅ Multi-redemption support (gift card style)
- ✅ Assignment limits per user
- ✅ Audit trail via redemption history
- ✅ State machine for coupon lifecycle

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Auth**: JWT (optional)
- **Testing**: Pytest

## Project Structure

```
coupon-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── coupon.py
│   │   └── redemption_history.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── coupon.py
│   │   └── redemption.py
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── books.py
│   │   │   ├── coupons.py
│   │   │   ├── assignments.py
│   │   │   └── users.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── book_service.py
│   │   ├── coupon_service.py
│   │   ├── assignment_service.py
│   │   ├── redemption_service.py
│   │   └── code_generator.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── enums.py
│       └── exceptions.py
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_books.py
│   ├── test_coupons.py
│   └── test_redemptions.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip or poetry

### Setup

1. Clone the repository
```bash
git clone <repo-url>
cd coupon-service
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run database migrations
```bash
alembic upgrade head
```

6. Start the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key API Endpoints

### Coupon Books

- `POST /api/v1/books` - Create coupon book
- `GET /api/v1/books/{bookId}` - Get book details
- `POST /api/v1/books/{bookId}/codes/generate` - Generate codes
- `POST /api/v1/books/{bookId}/codes/upload` - Upload codes

### Coupon Assignment

- `POST /api/v1/coupons/assign` - Assign random coupon
- `POST /api/v1/coupons/assign/{code}` - Assign specific coupon
- `GET /api/v1/users/{userId}/coupons` - Get user's coupons

### Coupon Redemption

- `POST /api/v1/coupons/lock/{code}` - Lock coupon for redemption
- `POST /api/v1/coupons/unlock/{code}` - Unlock coupon
- `POST /api/v1/coupons/redeem/{code}` - Redeem coupon

## Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/coupon_db

# App Settings
APP_NAME=Coupon Book Service
DEBUG=True
API_VERSION=v1

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Concurrency
LOCK_TIMEOUT_SECONDS=300
MAX_RETRY_ATTEMPTS=3
```

## Database Schema

See [entities.plantuml](../entities.plantuml) and [architecture_decisions.md](../architecture_decisions.md) for detailed data model.

## Concurrency Control

Uses PostgreSQL advisory locks:
- `pg_try_advisory_lock()` for atomic lock acquisition
- Automatic cleanup on connection disconnect
- Lock state tracked in coupon table for visibility

## Testing

Run tests:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Docker Deployment

Start with Docker Compose:
```bash
docker-compose up -d
```

This starts:
- FastAPI app on port 8000
- PostgreSQL on port 5432
- pgAdmin on port 5050 (optional)

## Performance Considerations

- Database connection pooling
- Query optimization with proper indexes
- Redis caching for frequently accessed data (optional)
- Background jobs for lock cleanup
- Rate limiting to prevent abuse

## License

MIT
