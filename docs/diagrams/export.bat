@echo off
REM Export PlantUML Diagrams Script for Windows
REM Converts all .puml files to PNG and SVG formats

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set DIAGRAMS_DIR=%SCRIPT_DIR%
set OUTPUT_DIR=%SCRIPT_DIR%exported

echo ================================================
echo    PlantUML Diagram Export Script (Windows)
echo ================================================
echo.

REM Check if PlantUML is installed
where plantuml >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] PlantUML not found in PATH
    echo.
    echo Please install PlantUML:
    echo 1. Download from: https://plantuml.com/download
    echo 2. Or install via Chocolatey: choco install plantuml
    echo.
    pause
    exit /b 1
)

echo [OK] PlantUML found
echo.

REM Create output directories
if not exist "%OUTPUT_DIR%\png" mkdir "%OUTPUT_DIR%\png"
if not exist "%OUTPUT_DIR%\svg" mkdir "%OUTPUT_DIR%\svg"

echo Output directory: %OUTPUT_DIR%
echo.

REM Count .puml files
set count=0
for %%f in ("%DIAGRAMS_DIR%\*.puml") do set /a count+=1
echo Found %count% diagram(s) to export
echo.

REM Export to PNG
echo Exporting to PNG...
plantuml -tpng -o "%OUTPUT_DIR%\png" "%DIAGRAMS_DIR%\*.puml"
echo [OK] PNG export complete
echo.

REM Export to SVG
echo Exporting to SVG...
plantuml -tsvg -o "%OUTPUT_DIR%\svg" "%DIAGRAMS_DIR%\*.puml"
echo [OK] SVG export complete
echo.

REM List exported files
echo ================================================
echo Exported files:
echo.
echo PNG files:
dir /b "%OUTPUT_DIR%\png\*.png" 2>nul
echo.
echo SVG files:
dir /b "%OUTPUT_DIR%\svg\*.svg" 2>nul
echo.

echo ================================================
echo [SUCCESS] Export complete!
echo.
echo PNG files: %OUTPUT_DIR%\png\
echo SVG files: %OUTPUT_DIR%\svg\
echo.
echo TIP: SVG files are vector graphics and scale perfectly
echo ================================================
echo.

pause
