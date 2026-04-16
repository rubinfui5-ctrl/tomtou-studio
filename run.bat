@echo off
REM ============================================================
REM  SOLOMON EMPIRE - WINDOWS LAUNCHER
REM  Double-click this to start ALL 10 systems
REM ============================================================
cls
echo.
echo  ============================================================
echo   SOLOMON EMPIRE - LAUNCHING ALL SYSTEMS
echo   Daily Target: $1,428  Weekly Target: $10,000
echo   @rubinfuimaono  deals.thatsonmeandyou.com
echo  ============================================================
echo.

REM --- Pre-flight check ---
python startup-check.py
if errorlevel 1 (
    echo.
    echo  Pre-flight failed. Run setup.bat first!
    pause
    exit /b 1
)

echo.
echo  Starting all systems (10 windows will open)...
echo.

echo  [1/10] Revenue Tracker
start "Solomon - Revenue Tracker" cmd /k "python revenue_tracker.py"
timeout /t 1 /nobreak >nul

echo  [2/10] Content Generator
start "Solomon - Content Generator" cmd /k "python content_generator.py"
timeout /t 1 /nobreak >nul

echo  [3/10] Email Marketing
start "Solomon - Email Marketing" cmd /k "python email_marketing.py"
timeout /t 1 /nobreak >nul

echo  [4/10] Market Intelligence
start "Solomon - Market Intelligence" cmd /k "python market_intelligence.py"
timeout /t 1 /nobreak >nul

echo  [5/10] Shopify Integration
start "Solomon - Shopify Integration" cmd /k "python shopify_integration.py"
timeout /t 1 /nobreak >nul

echo  [6/10] API Server (port 5001)
start "Solomon - API Server" cmd /k "python api-server.py"
timeout /t 2 /nobreak >nul

echo  [7/10] Mission Control Hub (port 8080)
start "Solomon - Mission Control" cmd /k "python mission_control_hub.py"
timeout /t 2 /nobreak >nul

echo  [8/10] Master Control (port 5002)
start "Solomon - Master Control" cmd /k "python master-control.py"
timeout /t 2 /nobreak >nul

echo  [9/10] Agent Dashboard (port 5003)
start "Solomon - Dashboard" cmd /k "python mission_control_dashboard.py"
timeout /t 1 /nobreak >nul

echo  [10/10] Empire Automation
start "Solomon - Empire Auto" cmd /k "python empire-auto.py"
timeout /t 2 /nobreak >nul

echo.
echo  ============================================================
echo   ALL SYSTEMS STARTED
echo  ============================================================
echo.
echo  Open these in your browser:
echo.
echo    Main Dashboard:  http://localhost:8080
echo    Agent Monitor:   http://localhost:5003
echo    Master Control:  http://localhost:5002
echo    API Status:      http://localhost:5001/status
echo.
echo  To stop: close the 10 command windows
echo.
echo  ============================================================
echo.
pause
