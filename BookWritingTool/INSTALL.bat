@echo off
REM BookWritingTool Installation Script
REM This script installs UV and all dependencies

echo ========================================
echo BookWritingTool Installation
echo ========================================
echo.

echo Step 1: Installing UV package manager...
echo.

REM Check if UV is already installed
where uv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo UV is already installed.
    echo.
) else (
    echo Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install UV
        pause
        exit /b 1
    )
    echo UV installed successfully!
    echo.
)

echo Step 2: Installing Python dependencies...
echo This may take several minutes...
echo.

uv sync

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 3: Installing Playwright browsers...
echo.

uv run playwright install chromium

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Playwright browser installation failed
    echo Bestseller scraping may not work
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run START_BOOK_WRITER.bat to launch the application.
echo.
echo Next steps:
echo 1. Get your API keys:
echo    - Claude: https://console.anthropic.com/
echo    - OpenAI: https://platform.openai.com/api-keys
echo 2. Launch the app with START_BOOK_WRITER.bat
echo 3. Enter your API keys in Settings tab
echo.
pause
