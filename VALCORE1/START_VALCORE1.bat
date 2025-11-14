@echo off
REM VALCORE1 Client Startup Script
REM Run this to start the VALCORE1 client on Windows

echo ===================================
echo    VALCORE1 CLIENT BRAIN
echo ===================================
echo.

cd /d "%~dp0\01_Client_Brain"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install/update requirements
echo Checking dependencies...
pip install -q -r setup\requirements_client.txt
echo.

REM Start VALCORE1
echo Starting VALCORE1...
echo Say "Hey Val" to activate
echo Press Ctrl+C to stop
echo.

python main_client.py

pause
