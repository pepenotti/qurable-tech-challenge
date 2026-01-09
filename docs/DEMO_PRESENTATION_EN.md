---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

<!-- _class: lead -->

# 🎫 Coupon Book Service

### Full Implementation of Design Challenge

**Challenge**: Design API + Pseudoc## 🚀 Production Readiness & Deployment Options

### Deployment Approaches

**1. Monolithic (Simple Start)**
- ECS Fargate or AWS App Runner
- RDS PostgreSQL Multi-AZ
- CloudFront + S3 for frontend
- ✅ Simple, cost-effective, handles significant load

**2. Microservices (Scale & Teams)**
- Auth Service + Coupon Service + Redemption Service
- Independent scaling and deployment
- Event-driven communication (SQS/EventBridge)
- ✅ Better for large orgs, independent teams

**3. Serverless (Variable Load)**
- Lambda functions + API Gateway
- Aurora Serverless or DynamoDB
- Auto-scale to zero, pay per request
- ✅ Perfect for spiky traffic, minimal ops

**Production Additions** (any approach):
- CloudWatch metrics & X-Ray tracing
- Secrets Manager for credentials
- Rate limiting & DDoS protection
- Database backups & DR plan

**Architecture is deployment-agnostic** - clean boundaries enable any model 🎯e  
**Delivered**: Complete working application

**Built with**: FastAPI • Vue 3 • PostgreSQL • Docker

---

## 📋 The Challenge

**What was asked**: API design + pseudocode + architecture

**Core Requirements**:
- ✅ Coupon books with code upload/generation
- ✅ Random coupon assignment with concurrency handling
- ✅ Lock mechanism for redemption
- ✅ Multi-redemption support (book level)
- ✅ Max assignments per user (book level)

**Key Technical Challenges**:
1. Database locking and state management
2. Randomness logic under concurrent load
3. Prevent race conditions and data integrity

**What I delivered**: Fully working implementation (not just design docs) ⭐

---

## 🛠️ Tech Stack

| Layer | Technology | Why? |
|-------|-----------|------|
| **Backend** | FastAPI + Python 3.11 | Async/await, auto docs, type safety |
| **Database** | PostgreSQL 15 | ACID, advisory locks, row locking |
| **ORM** | SQLAlchemy 2.0 (async) | Modern async patterns |
| **Frontend** | Vue 3 + Pinia | Reactive, lightweight, modern |
| **Infrastructure** | Docker Compose | Consistent environments |

**Every choice was deliberate** - optimized for concurrency, data integrity, and developer experience.

---

## 🏗️ Architecture Overview

![Architecture Diagram](diagrams/exported/png/System%20Architecture.png)

**3-Tier Design**:
- Frontend: Vue 3 SPA
- Backend: FastAPI with async services
- Data: PostgreSQL with connection pooling

**Deployment Flexibility**:
- 📦 **Monolithic**: ECS/App Runner (simple, cost-effective)
- 🔷 **Microservices**: Separate auth, coupon, redemption services
- ⚡ **Serverless**: Lambda + API Gateway + Aurora Serverless

**Key Principle**: Stateless, service-separated, deployment-agnostic

---

## 🗄️ Database Schema

![Database Schema](diagrams/exported/png/Database%20Schema.png)

---

## 📊 Database Schema (Detail)

**6 Tables**:
- **Users**: Authentication (JWT, bcrypt, roles)
- **Books**: Coupon book configuration
- **Coupons**: State machine core (14 fields)
- **RedemptionHistory**: Audit trail
- **UserPools**: Bulk distribution groups
- **pool_users**: Many-to-many association

**Design Highlights**:
- Proper indexes on foreign keys and state
- CASCADE deletes where appropriate
- JSONB for flexible metadata

---

## 🔄 State Machine

![State Machine](diagrams/exported/png/State%20Machine.png)

---

## 🔄 State Machine (Explained)

```
UNASSIGNED → ASSIGNED → LOCKED → REDEEMED
              ↑           ↓
              └───────────┘ (unlock on timeout)
```

**Key Transitions**:
- **Assign**: Claim a coupon (with validation)
- **Lock**: Prepare for redemption (5 min timeout)
- **Redeem**: Finalize (permanent, logged)
- **Unlock**: Automatic timeout (prevents deadlocks)

**Every transition is validated** - prevents all edge cases

---

## ✨ Key Features

### Required (Challenge Specs)
- � **Random Assignment** - With SELECT FOR UPDATE SKIP LOCKED
- ♻️ **Multi-Redemption** - Configurable per book
- � **Max Assignments** - Per user, per book
- 📤 **Code Upload/Generation** - CSV upload or pattern-based
- 🔒 **Lock Mechanism** - Temporary lock before redeem
- 🔄 **State Machine** - UNASSIGNED → ASSIGNED → LOCKED → REDEEMED

### Bonus (Production Additions)
- 🔐 **JWT Authentication** - Role-based access (ADMIN/USER)
- 🎨 **Vue 3 Frontend** - Full UI implementation
- 📦 **User Pools** - Bulk distribution (equal/random modes)
- 📝 **Audit Trail** - Complete redemption history
- ✅ **Test Suite** - Comprehensive validation scripts

**From design doc to working product** 🚀

---

## 📊 Challenge Requirements vs Delivery

| Requirement | Asked For | Delivered |
|------------|-----------|-----------|
| System Architecture | High-level design | ✅ + Detailed diagrams |
| Database Design | High-level schema | ✅ + Full implementation |
| API Endpoints | Design + formats | ✅ + Working FastAPI |
| Pseudocode | 3 key operations | ✅ + Production code |
| Deployment Strategy | High-level plan | ✅ + Docker + AWS docs |
| **Frontend** | ❌ Not required | ✅ Full Vue 3 app |
| **Authentication** | ❌ Not specified | ✅ JWT + RBAC |
| **Testing** | ❌ Not required | ✅ Test suite |
| **Documentation** | Basic | ✅ 11 docs + 8 diagrams |

**I turned a design exercise into a production-ready demo** 💪

---

## ⚡ Concurrency Solution

**The Problem**: 1000 users, 100 codes left. No duplicates. No race conditions.

**The Solution**:
```python
# PostgreSQL advisory locks + SKIP LOCKED
async with session.begin():
    # 1. Acquire book-level advisory lock
    await session.execute(text("SELECT pg_advisory_lock(:book_id)"), 
                          {"book_id": book_hash})
    
    # 2. SELECT FOR UPDATE SKIP LOCKED
    coupon = await session.execute(
        select(Coupon)
        .where(Coupon.book_id == book_id, Coupon.state == 'UNASSIGNED')
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    
    # 3. Assign atomically
    coupon.state = 'ASSIGNED'
    coupon.assigned_user_id = user_id
```

**Result**: Scales perfectly under concurrent load 🚀

---

## 🧪 Concurrency Demo

![Sequence Diagram](diagrams/exported/png/Assign%20Random%20Coupon.png)

**Validated with concurrent test scripts** - 100 simultaneous requests ✅

---

## 💻 API Highlights

**Modern Python Patterns**:
- ✅ Async/await everywhere
- ✅ Pydantic for validation
- ✅ Service layer for business logic
- ✅ Custom exceptions → HTTP codes
- ✅ Comprehensive error messages
- ✅ OpenAPI docs at `/docs`

**Code Quality**:
- Type hints throughout
- Clean separation of concerns
- Testable and maintainable

---

## 🎨 Frontend Demo

**Live Demo Time!** 

**Flow**:
1. Login as admin
2. Create a coupon book
3. Upload codes (CSV)
4. Distribute to user pool
5. Switch to user account
6. Lock and redeem coupon

**UX Features**:
- Toast notifications (non-blocking)
- Real-time state updates
- Lock countdown timers
- Color-coded feedback

---

## ✅ Testing & Quality

**Test Coverage**:
- `showcase_tests.sh` - Comprehensive integration tests
- Concurrent request simulation
- Error case validation
- State machine edge cases

**Error Handling**:
- Database exceptions → user-friendly messages
- Validation before DB hits
- Actionable error responses

**Documentation**:
- 8 PlantUML diagrams
- Comprehensive README files
- Inline code documentation

---

## 🎓 Lessons Learned

**Technical Insights**:
1. PostgreSQL concurrency features are incredibly powerful
2. State machines make business logic bulletproof
3. FastAPI's async capabilities shine in I/O workloads
4. Good documentation = good code

**What I'd Improve**:
- Add comprehensive logging earlier
- Set up CI/CD from day one
- Consider Redis for distributed locking
- Add more frontend unit tests

---

## 🚀 Production Readiness

**Infrastructure** (Ready to deploy):
- AWS ECS Fargate (backend)
- RDS PostgreSQL Multi-AZ (database)
- CloudFront + S3 (frontend)
- Application Load Balancer

**Still Needed**:
- CloudWatch metrics & logs
- AWS Secrets Manager
- Rate limiting
- SSL everywhere
- Database backups
- Disaster recovery plan

**The hard part (business logic) is done** ✅

---

## 📊 Project Metrics

**Code**:
- Backend: ~3,000 lines of Python
- Frontend: ~2,000 lines of Vue/TypeScript
- Database: 6 tables, 8 relationships
- API: 20+ endpoints

**Documentation**:
- 11 markdown files (organized)
- 8 PlantUML diagrams
- Comprehensive getting started guide

**Time Investment**: [X hours]
- Implementation: [Y%]
- Testing & Polish: [Z%]
- Documentation: [W%]

---

<!-- _class: lead -->

## 🙏 Thank You!

### Questions?

**GitHub**: [Your repo link]
**Email**: [Your email]

**Try it yourself**:
```bash
git clone [repo]
cd qble/coupon-service
docker-compose up -d
cd frontend && npm install && npm run dev
# Open http://localhost:5173
```

**Ready in under 5 minutes** 🚀

---

## 📚 Backup Slides

(Additional technical details if needed)

---

## Redemption Flow Detail

![Redeem Coupon](diagrams/exported/png/Redeem%20Coupon.png)

**Key Steps**:
1. Validate lock ownership
2. Check lock expiration
3. Verify redemption count
4. Update state atomically
5. Log to RedemptionHistory
6. Commit or rollback

---

## AWS Deployment Architecture

![AWS Deployment](diagrams/exported/png/AWS%20Deployment.png)

**Production Setup**:
- Auto-scaling backend
- Multi-AZ database
- CloudWatch monitoring
- VPC security

---

<!-- _class: lead -->

# Questions?

I'm happy to dive deeper into any aspect:
- Architecture decisions
- Implementation details
- Trade-offs and alternatives
- Scaling considerations
- Production deployment
