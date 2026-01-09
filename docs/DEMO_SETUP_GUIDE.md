# 🎬 Demo Presentation Setup Guide

This folder contains everything you need for your demo presentation.

---

## 📁 Files Included

1. **`DEMO_TALK_SCRIPT.md`** - Complete talk script (10-15 min)
   - Slide-by-slide script with timing
   - Delivery tips and best practices
   - Common Q&A with suggested answers
   - Presentation tool recommendations

2. **`DEMO_PRESENTATION.md`** - Marp slideshow (ready to use!)
   - 20+ slides with your content
   - References your exported diagrams
   - Technical deep-dives included
   - Backup slides for Q&A

---

## 🚀 Quick Start Options

### Option 1: Marp (Recommended) - Markdown Slides

**Install Marp**:
```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Or use VS Code extension
code --install-extension marp-team.marp-vscode
```

**Generate Presentation**:
```bash
cd qble/

# Generate HTML (with speaker notes)
marp DEMO_PRESENTATION.md -o demo-slides.html

# Generate PDF (for sharing)
marp DEMO_PRESENTATION.md -o demo-slides.pdf

# Generate PowerPoint
marp DEMO_PRESENTATION.md -o demo-slides.pptx

# Watch mode (auto-regenerate on save)
marp DEMO_PRESENTATION.md -w --html
```

**Present**:
```bash
# Open the generated HTML in your browser
open demo-slides.html

# Use arrow keys to navigate
# Press 'F' for fullscreen
# Press 'P' for presenter mode (with notes)
```

---

### Option 2: VS Code Extension (Live Preview)

**Setup**:
1. Install "Marp for VS Code" extension
2. Open `DEMO_PRESENTATION.md`
3. Click "Open Preview to the Side" (or `Ctrl+K V`)
4. Edit and see changes live!

**Present**:
- Export to HTML/PDF from VS Code
- Or use the preview directly (fullscreen mode)

---

### Option 3: reveal.js (Advanced)

**Setup**:
```bash
# Clone reveal.js
git clone https://github.com/hakimel/reveal.js.git demo-reveal
cd demo-reveal
npm install

# Copy your content
# Edit index.html with slides from DEMO_PRESENTATION.md
# Add your diagrams to the images folder

# Start server
npm start

# Open http://localhost:8000
```

**Benefits**:
- Beautiful transitions
- More control over layout
- Can embed live code examples
- Professional look

---

### Option 4: Google Slides (Quick & Easy)

**Setup**:
1. Go to slides.google.com
2. Create new presentation
3. Use DEMO_TALK_SCRIPT.md as your guide
4. Upload exported diagrams from `diagrams/exported/png/`
5. Add code snippets as images or text boxes

**Benefits**:
- Familiar interface
- Easy to share
- Works anywhere
- Collaborate with others

---

## 📊 Diagram Files to Use

Your exported diagrams are ready in `diagrams/exported/png/`:

1. **System Architecture.png** - Slide 4
2. **Database Schema.png** - Slide 5
3. **State Machine.png** - Slide 6
4. **Assign Random Coupon.png** - Slide 8 (concurrency)
5. **Redeem Coupon.png** - Backup slide
6. **AWS Deployment.png** - Slide 13

**For Marp**: The paths are already set in `DEMO_PRESENTATION.md`  
**For Others**: Drag and drop these PNG files into your slides

---

## 🎯 Presentation Flow

### Recommended Timing (15 minutes total)

| Slide | Topic | Time | Notes |
|-------|-------|------|-------|
| 1 | Title | 0:30 | Intro yourself |
| 2 | Challenge | 1:00 | Set context |
| 3 | Tech Stack | 1:00 | Justify choices |
| 4 | Architecture | 1:00 | High-level design |
| 5-6 | Database & State | 3:00 | Core concepts |
| 7 | Features | 1:00 | What it does |
| 8-9 | Concurrency | 2:00 | **Technical highlight** |
| 10 | API Highlights | 1:00 | Code quality |
| 11 | Frontend Demo | 2:00 | **Live demo** |
| 12 | Testing | 1:00 | Quality assurance |
| 13 | Lessons | 1:00 | Reflection |
| 14 | Production | 0:30 | Next steps |
| 15 | Q&A | - | Open floor |

---

## 🎬 Before Your Demo

### 1 Week Before
- [ ] Review DEMO_TALK_SCRIPT.md
- [ ] Practice presentation once
- [ ] Verify all diagrams export correctly

### 3 Days Before
- [ ] Practice presentation 3 times
- [ ] Time yourself
- [ ] Prepare for Q&A (review common questions)

### 1 Day Before
- [ ] Generate final slides (HTML/PDF)
- [ ] Test live demo environment
- [ ] Take backup screenshots
- [ ] Verify docker-compose works

### 1 Hour Before
- [ ] Start docker-compose
- [ ] Open demo in browser (test it works)
- [ ] Open slides in presentation mode
- [ ] Test audio/video (if remote)
- [ ] Close unnecessary apps
- [ ] Turn off notifications

---

## 💡 Pro Tips

### For the Live Demo

**Before you start**:
```bash
# Start everything
cd qurable-tech-challenge
docker-compose up -d
cd frontend
npm run dev

# Verify it's working
open http://localhost:5173
```

**Demo Safety Nets**:
1. Have the database pre-populated with test data
2. Keep backup screenshots ready
3. Test the exact demo flow 3 times before
4. Have `showcase_tests.sh` ready to run if needed
5. Know how to restart if something breaks

**If Demo Breaks**:
- Stay calm
- Switch to screenshots
- Explain what should happen
- Offer to show afterward

### For Questions

**Golden Rule**: It's okay to say "I don't know, but I'd research X"

**Common Question Types**:
1. **Technical Deep-Dive**: Be ready to show code
2. **Scale Questions**: Talk about horizontal scaling
3. **Alternative Approaches**: Show you considered trade-offs
4. **Production**: Discuss monitoring, logging, CI/CD

**Have Ready**:
- GitHub repo link
- Specific code files you might show
- Diagram PNGs for detailed discussion

---

## 🎤 Delivery Best Practices

### Speaking
- ✅ Speak clearly and pace yourself
- ✅ Pause after technical points (let it sink in)
- ✅ Make eye contact (or look at camera)
- ✅ Show enthusiasm - you built this!
- ✅ Use "we" not "I" when appropriate (team mentality)

### Slides
- ✅ Don't read slides verbatim
- ✅ Use slides as talking points
- ✅ Point to diagrams as you explain
- ✅ Advance slides smoothly
- ✅ Use presenter notes (if available)

### Demo
- ✅ Narrate what you're doing
- ✅ Show, don't just tell
- ✅ Highlight state transitions
- ✅ Point out toast notifications
- ✅ Connect UI actions to backend logic

---

## 🔧 Troubleshooting

### Marp won't install
```bash
# Try without -g
npm install @marp-team/marp-cli

# Or use npx directly
npx @marp-team/marp-cli DEMO_PRESENTATION.md -o slides.html
```

### Diagrams not showing in Marp
```bash
# Check the path is correct (relative to .md file)
# Paths should be: ./diagrams/exported/png/[filename].png

# Or use absolute paths
# Update DEMO_PRESENTATION.md with full paths
```

### Docker won't start
```bash
# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL

# Kill processes if needed
kill -9 [PID]

# Restart
docker-compose down
docker-compose up -d
```

### Live demo is slow
```bash
# Check logs
docker-compose logs -f app

# Restart backend
docker-compose restart app

# Check database
docker-compose ps
```

---

## 📚 Additional Resources

### Marp Documentation
- **Official Guide**: https://marp.app/
- **Syntax**: https://marpit.marp.app/markdown
- **Themes**: https://github.com/marp-team/marp-core/tree/main/themes

### Presentation Skills
- **Technical Talks**: https://speaking.io/
- **Demo Tips**: https://www.youtube.com/watch?v=iE9y3gyF8Kw

### Your Project Docs
- **DEMO_TALK_SCRIPT.md** - Full script with timing
- **README.md** - Project overview
- **SHOWCASE_GUIDE.md** - Feature walkthrough
- **diagrams/README.md** - Diagram documentation

---

## ✅ Final Checklist

Before presenting:

**Content Ready**:
- [ ] Slides generated (HTML or PDF)
- [ ] All diagrams embedded correctly
- [ ] Talk script reviewed
- [ ] Q&A prep done

**Demo Environment**:
- [ ] Docker containers running
- [ ] Frontend accessible
- [ ] Database populated
- [ ] Backup screenshots ready

**Technical Setup**:
- [ ] Presentation software tested
- [ ] Dual monitors configured (if available)
- [ ] Audio/video working (if remote)
- [ ] Notifications disabled
- [ ] Internet connection stable

**Personal**:
- [ ] Practiced 3+ times
- [ ] Timed yourself
- [ ] Comfortable with content
- [ ] Confident and ready!

---

## 🎉 You're Ready!

Your presentation materials are professional, comprehensive, and ready to impress.

**Remember**:
- You built something impressive
- You understand it deeply
- You documented it well
- You're ready to answer questions

**Go show them what you've built!** 🚀

---

**Questions about setup?** Check:
1. DEMO_TALK_SCRIPT.md - Detailed instructions
2. Marp documentation - https://marp.app/
3. Your diagrams - All exported and ready in diagrams/exported/png/

**Good luck!** 🍀
