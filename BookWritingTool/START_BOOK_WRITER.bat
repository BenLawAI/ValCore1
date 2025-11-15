@echo off
REM BookWritingTool Launcher for Windows
REM This script launches the Book Writing Tool application

echo ========================================
echo BookWritingTool - Professional Writing Suite
echo ========================================
echo.

REM Check if UV is installed
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: UV package manager not found!
    echo Please run INSTALL.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Starting BookWritingTool...
echo.

uv run python app/main.py

REM If app exits with error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%
    pause
)
