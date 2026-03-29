@echo off
REM ArthaSetu - Start Server (Windows Batch File)

color 0A
cls

echo.
echo ============================================================
echo   ArthaSetu - Real-Time Stock Investment Intelligence
echo   Launching Flask Server on localhost:5000
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check dependencies
echo [*] Checking dependencies...
python -c "import flask; import flask_cors" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing Flask dependencies...
    python -m pip install flask flask-cors -q
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)
echo [OK] All dependencies ready
echo.

REM Display startup info
echo ============================================================
echo [*] SERVER STARTING
echo ============================================================
echo.
echo   URL:  http://localhost:5000
echo   API:  http://localhost:5000/api
echo.
echo [*] DEMO LOGIN
echo    Email: demo@arthsetu.com
echo    Password: demo123
echo.
echo [*] FEATURES
echo    - Real-time stock analysis
echo    - Multi-agent AI system
echo    - User authentication
echo    - Portfolio management
echo    - Beautiful dashboard
echo.
echo ============================================================
echo Press Ctrl+C to stop server
echo ============================================================
echo.

REM Start server
python start_server.py

if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start
    echo Check the error messages above
    pause
)
