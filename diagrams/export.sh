#!/bin/bash

# Export PlantUML Diagrams Script
# Converts all .puml files to PNG and SVG formats

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIAGRAMS_DIR="$SCRIPT_DIR"
OUTPUT_DIR="$SCRIPT_DIR/exported"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PlantUML Diagram Export Script              ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo ""

# Check if PlantUML is installed
if ! command -v plantuml &> /dev/null; then
    echo -e "${YELLOW}⚠️  PlantUML not found. Installing...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install plantuml
        else
            echo -e "${YELLOW}Please install Homebrew first: https://brew.sh/${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y plantuml
    else
        echo -e "${YELLOW}Please install PlantUML manually: https://plantuml.com/download${NC}"
        exit 1
    fi
fi

# Create output directories
mkdir -p "$OUTPUT_DIR/png"
mkdir -p "$OUTPUT_DIR/svg"

echo -e "${GREEN}✓ PlantUML found${NC}"
echo -e "${BLUE}📁 Output directory: $OUTPUT_DIR${NC}"
echo ""

# Count .puml files
PUML_COUNT=$(find "$DIAGRAMS_DIR" -maxdepth 1 -name "*.puml" | wc -l)
echo -e "${BLUE}📊 Found $PUML_COUNT diagram(s) to export${NC}"
echo ""

# Export to PNG
echo -e "${YELLOW}🖼️  Exporting to PNG...${NC}"
plantuml -tpng -o "$OUTPUT_DIR/png" "$DIAGRAMS_DIR"/*.puml
echo -e "${GREEN}✓ PNG export complete${NC}"
echo ""

# Export to SVG
echo -e "${YELLOW}🎨 Exporting to SVG...${NC}"
plantuml -tsvg -o "$OUTPUT_DIR/svg" "$DIAGRAMS_DIR"/*.puml
echo -e "${GREEN}✓ SVG export complete${NC}"
echo ""

# List exported files
echo -e "${BLUE}📋 Exported files:${NC}"
echo ""
echo -e "${GREEN}PNG files:${NC}"
ls -lh "$OUTPUT_DIR/png"/*.png 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo -e "${GREEN}SVG files:${NC}"
ls -lh "$OUTPUT_DIR/svg"/*.svg 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✅ Export complete!${NC}"
echo ""
echo -e "PNG files: ${OUTPUT_DIR}/png/"
echo -e "SVG files: ${OUTPUT_DIR}/svg/"
echo ""
echo -e "${BLUE}💡 Tip: SVG files are vector graphics and scale perfectly${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
