@echo off
REM ============================================================
REM  SOLOMON EMPIRE - WINDOWS SETUP (run this ONCE)
REM ============================================================
cls
echo.
echo  ============================================================
echo   SOLOMON EMPIRE - SETUP
echo  ============================================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Download from: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during install!
    pause
    exit /b 1
)
echo  [1/4] Python found:
python --version

REM --- Install packages ---
echo.
echo  [2/4] Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo  ERROR: Package installation failed.
    echo  Try running: pip install Flask Flask-CORS requests python-dotenv psutil
    pause
    exit /b 1
)
echo  Packages installed.

REM --- Create directories ---
echo.
echo  [3/4] Creating data directories...
if not exist "data"                     mkdir data
if not exist "data\generated_content"   mkdir data\generated_content
if not exist "data\email_marketing"     mkdir data\email_marketing
if not exist "data\market_intelligence" mkdir data\market_intelligence
if not exist "data\shopify"             mkdir data\shopify
if not exist "data\reports"             mkdir data\reports
if not exist "logs\empire"              mkdir logs\empire
if not exist "memory"                   mkdir memory
echo  Directories ready.

REM --- Pre-flight check ---
echo.
echo  [4/4] Running pre-flight check...
python startup-check.py
if errorlevel 1 (
    echo.
    echo  Fix the issues above then run setup.bat again.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   SETUP COMPLETE!
echo  ============================================================
echo.
echo  Next: Run  run.bat  to start all 10 systems.
echo.
pause
