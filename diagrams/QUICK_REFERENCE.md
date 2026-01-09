# 📊 Diagram Quick Reference

Essential commands and tips for working with PlantUML diagrams.

---

## 🚀 Quick Export

### Export All Diagrams (One Command)

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

**Output:**
- PNG images → `exported/png/`
- SVG images → `exported/svg/`

---

## � Available Diagrams

| # | Diagram | File | Best For |
|---|---------|------|----------|
| 1 | System Architecture | `architecture.puml` | Presentations, overview |
| 2 | Database Schema | `database-schema.puml` | Data modeling, ER discussions |
| 3 | Coupon State Machine | `state-machine.puml` | Business logic, validation |
| 4 | Assign Random Coupon | `sequence-assign-random.puml` | Concurrency explanation |
| 5 | Lock Coupon | `sequence-lock-coupon.puml` | Lock mechanism details |
| 6 | Redeem Coupon | `sequence-redeem-coupon.puml` | Core transaction flow |
| 7 | Upload Codes | `sequence-upload-codes.puml` | Bulk operations |
| 8 | AWS Deployment | `deployment-aws.puml` | Production infrastructure |

---

## 🎨 Viewing Options

### 1. VS Code (Best for editing)
```bash
# Install extension (one time)
code --install-extension jebbs.plantuml

# Open and preview
code architecture.puml
# Press Alt+D (Windows/Linux) or Option+D (Mac)
```

### 2. Online Viewer (No installation)
1. Go to: https://www.plantuml.com/plantuml/uml/
2. Copy-paste `.puml` file content
3. View instantly

### 3. Command Line (Export to images)
```bash
# Install PlantUML first
brew install plantuml        # macOS
apt-get install plantuml     # Linux
choco install plantuml       # Windows

# Generate images
plantuml architecture.puml   # Single PNG
plantuml -tsvg *.puml        # All as SVG
plantuml *.puml              # All as PNG
```

---

## 💡 Pro Tips

### For Presentations
✅ Use SVG format (scales perfectly)
```bash
plantuml -tsvg *.puml
```

### For Documentation
✅ Use PNG format (universal compatibility)
```bash
plantuml *.puml
```

### For Live Editing
✅ Use VS Code with PlantUML extension
- Real-time preview as you type
- Syntax highlighting
- Auto-completion

### For Quick Sharing
✅ Use online PlantUML viewer
- No installation required
- Instant rendering
- Share URL directly

---

## 🔧 Customization Examples

Want to modify diagram appearance? Edit any `.puml` file:

```plantuml
' Change background
skinparam backgroundColor #F5F5F5

' Change fonts
skinparam defaultFontName Helvetica
skinparam defaultFontSize 12

' Change colors
skinparam componentBackgroundColor LightSkyBlue
skinparam databaseBackgroundColor LightGreen
skinparam sequenceArrowColor Navy
```

---

## 📦 Export Script Features

The included scripts (`export.sh` / `export.bat`) automatically:

✅ Check for PlantUML installation  
✅ Install PlantUML if missing (macOS only)  
✅ Create output directories  
✅ Export to both PNG and SVG  
✅ Display file sizes  
✅ Show completion summary  

---

## 🎯 Common Workflows

### Technical Interview Demo
```bash
# 1. Open architecture diagram
code architecture.puml

# 2. Walk through system design with live preview
# Press Alt+D to show diagram side-by-side

# 3. Show specific flows
code sequence-redeem-coupon.puml
```

### Documentation Update
```bash
# 1. Export all diagrams
./export.sh

# 2. Reference in README
# ![Architecture](diagrams/exported/png/architecture.png)

# 3. Commit both .puml sources and exported images
git add diagrams/
git commit -m "Update architecture diagrams"
```

### Code Review / PR
```bash
# 1. Export relevant diagram
plantuml state-machine.puml

# 2. Upload to PR description
# 3. Link to source .puml file for context
```

### Presentation Slides
```bash
# 1. Export as SVG for crisp scaling
plantuml -tsvg architecture.puml

# 2. Import into PowerPoint/Keynote/Google Slides
# 3. Scale without any quality loss
```

---

## 📚 Additional Resources

### PlantUML Documentation
- **Official Guide**: https://plantuml.com/
- **Sequence Diagrams**: https://plantuml.com/sequence-diagram
- **State Diagrams**: https://plantuml.com/state-diagram
- **Class Diagrams**: https://plantuml.com/class-diagram
- **Component Diagrams**: https://plantuml.com/component-diagram

### Project Documentation
- **Main README**: `../README.md`
- **Setup Guide**: `../coupon-service/GETTING_STARTED.md`
- **Showcase Demo**: `../coupon-service/docs/SHOWCASE_GUIDE.md`
- **Full Diagram Docs**: `./README.md`

---

**Last Updated**: January 9, 2026  
**Format**: PlantUML (`.puml`)  
**Export Formats**: PNG, SVG, PDF, LaTeX  
**Total Diagrams**: 8
