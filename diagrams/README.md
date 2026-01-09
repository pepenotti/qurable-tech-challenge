# 🏗️ Coupon Book Service - Architecture Diagrams

This folder contains PlantUML diagrams documenting the system architecture, database schema, state machines, and key workflows.

## 📋 Diagram Files

| File | Description | Type |
|------|-------------|------|
| `architecture.puml` | System architecture overview | Component |
| `database-schema.puml` | Database schema with relationships | Class |
| `state-machine.puml` | Coupon lifecycle state machine | State |
| `sequence-assign-random.puml` | Assign random coupon flow | Sequence |
| `sequence-lock-coupon.puml` | Lock coupon flow | Sequence |
| `sequence-redeem-coupon.puml` | Redeem coupon flow | Sequence |
| `sequence-upload-codes.puml` | Upload code list flow | Sequence |
| `deployment-aws.puml` | AWS production deployment | Deployment |

## 🎨 How to View Diagrams

### Option 1: VS Code with PlantUML Extension (Recommended)

1. **Install the PlantUML extension:**
   ```bash
   code --install-extension jebbs.plantuml
   ```

2. **Open any `.puml` file**

3. **Preview the diagram:**
   - Press `Alt+D` (Windows/Linux) or `Option+D` (Mac)
   - Or right-click → "Preview Current Diagram"

### Option 2: Online Viewer (No Installation)

1. Go to https://www.plantuml.com/plantuml/uml/

2. Copy the content of any `.puml` file

3. Paste into the editor to see the rendered diagram

### Option 3: Export to PNG/SVG

**macOS/Linux:**
```bash
cd diagrams/
./export.sh
```

**Windows:**
```cmd
cd diagrams
export.bat
```

**Output Location:**
- PNG images: `exported/png/`
- SVG images: `exported/svg/`

### Option 4: Command Line (Manual Export)

Install PlantUML:
```bash
# macOS
brew install plantuml

# Ubuntu/Debian
apt-get install plantuml

# Windows
choco install plantuml
```

Generate images:
```bash
# From the diagrams/ directory

# Generate all PNGs
plantuml *.puml

# Generate all SVGs (vector, scalable)
plantuml -tsvg *.puml

# Generate specific diagram
plantuml architecture.puml
```

## 📦 Export Formats

PlantUML supports multiple output formats:
- PNG (default)
- SVG (vector, scalable)
- PDF
- ASCII art
- LaTeX

## 🔧 Customization

All diagrams use these common settings:
```plantuml
skinparam backgroundColor #FEFEFE
skinparam sequenceMessageAlign center
```

You can modify colors, fonts, and styles by editing the `skinparam` sections.

## 📚 Diagram Descriptions

### 1. **System Architecture** (`architecture.puml`)
High-level component diagram showing the 3-tier architecture:
- **Client Layer**: Users/API consumers
- **Application Tier**: FastAPI service with REST API
- **Data Tier**: PostgreSQL database
- **Deployment**: Docker containerization

**Use Case**: System overview, technical presentations

### 2. **Database Schema** (`database-schema.puml`)
Entity-Relationship (ER) diagram showing:
- **Tables**: Users, Books, Coupons, RedemptionHistory
- **Relationships**: Foreign keys and cardinality
- **Indexes**: Performance optimization points
- **Constraints**: Data integrity rules

**Use Case**: Database design, data modeling discussions

### 3. **Coupon State Machine** (`state-machine.puml`)
State transition diagram for coupon lifecycle:
```
UNASSIGNED → ASSIGNED → LOCKED → REDEEMED
              ↑           ↓
              └───────────┘ (unlock after timeout)
```

**Use Case**: Understanding business logic, validation rules

### 4. **Assign Random Coupon Flow** (`sequence-assign-random.puml`)
Detailed sequence diagram showing:
- Random coupon selection with `SELECT FOR UPDATE SKIP LOCKED`
- Concurrency handling with PostgreSQL row locking
- State validation and transitions
- Error scenarios

**Use Case**: Explaining concurrency strategy, code reviews

### 5. **Lock Coupon Flow** (`sequence-lock-coupon.puml`)
Sequence diagram for the locking mechanism:
- User requests to lock a coupon
- Validation (ownership, state, expiration)
- Setting lock with timeout
- Transaction safety

**Use Case**: Redemption flow preparation, timeout handling

### 6. **Redeem Coupon Flow** (`sequence-redeem-coupon.puml`)
Complete redemption transaction flow:
- Lock verification
- State machine validation
- Redemption counting (multi-redemption support)
- History logging with audit trail
- Transaction commit/rollback

**Use Case**: Core business logic explanation, demo flows

### 7. **Upload Code List Flow** (`sequence-upload-codes.puml`)
Bulk operations workflow:
- CSV/JSON code upload
- Validation and parsing
- Batch insertion with transaction safety
- Error handling and rollback

**Use Case**: Data import process, batch operations

### 8. **AWS Production Deployment** (`deployment-aws.puml`)
Production architecture on AWS:
- **Frontend**: Route 53 → CloudFront → S3 (static)
- **Backend**: ALB → ECS Fargate (auto-scaling)
- **Database**: RDS PostgreSQL (Multi-AZ)
- **Monitoring**: CloudWatch metrics and logs
- **Security**: VPC, Security Groups, IAM roles

**Use Case**: Production deployment planning, infrastructure discussions

## 🚀 Quick Start

### View a Diagram in VS Code
```bash
cd diagrams/
code architecture.puml
# Press Alt+D (Option+D on Mac) to preview
```

### Export All Diagrams
```bash
# macOS/Linux
./export.sh

# Windows
export.bat

# View exported images
open exported/png/architecture.png
```

### Manual Export (with PlantUML installed)
```bash
# Generate all as PNG
plantuml *.puml

# Generate all as SVG (vector graphics)
plantuml -tsvg *.puml

# Move to specific directory
plantuml -o ./exported/png *.puml
```

---

## 💡 Tips & Best Practices

### For Presentations
- **Use SVG**: Vector graphics scale perfectly at any size
- **Export**: `plantuml -tsvg *.puml` for crisp rendering
- **Embed**: SVG files work great in slides and web pages

### For Documentation
- **PNG works best**: Widely supported in Markdown and wikis
- **Reference**: Link to diagrams in your README files
- **Version control**: Commit both `.puml` source and exported images

### For Collaboration
- **VS Code**: Best for live editing with preview
- **Online viewer**: Share quick previews without installation
- **Draw.io**: Import PlantUML for visual editing if needed

### For Maintenance
- **Keep `.puml` files updated**: These are your source of truth
- **Re-export**: After editing, always regenerate images
- **Organize**: Use the `exported/` directory structure

---

## 📖 Learn More

### PlantUML Resources
- **Official Docs**: https://plantuml.com/
- **Sequence Diagrams**: https://plantuml.com/sequence-diagram
- **State Diagrams**: https://plantuml.com/state-diagram
- **Class Diagrams**: https://plantuml.com/class-diagram
- **Deployment Diagrams**: https://plantuml.com/deployment-diagram

### Project Documentation
- **Main README**: `../README.md` - Project overview
- **Getting Started**: `../coupon-service/GETTING_STARTED.md` - Setup guide
- **Showcase Guide**: `../coupon-service/docs/SHOWCASE_GUIDE.md` - Demo walkthrough
- **Implementation Status**: `../coupon-service/docs/IMPLEMENTATION_STATUS.md` - Feature checklist

---

## 🎯 Common Use Cases

These diagrams are perfect for:

✅ **Technical Presentations**: Explaining the system to stakeholders  
✅ **Documentation**: Embedding in README files and technical docs  
✅ **Code Reviews**: Discussing architecture decisions visually  
✅ **Onboarding**: Helping new team members understand the system  
✅ **Job Interviews**: Demonstrating your design and documentation skills  
✅ **API Documentation**: Showing request/response flows  
✅ **Debugging**: Tracing complex flows and identifying bottlenecks  

---

**Last Updated**: January 9, 2026  
**Format**: PlantUML (`.puml`)  
**Export Formats**: PNG, SVG, PDF, ASCII art, LaTeX  
**Diagram Count**: 8 comprehensive diagrams
