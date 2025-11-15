# VALCORE1 UV Setup Script for Windows
# This script automates the UV setup process

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VALCORE1 UV Setup for Windows Desktop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if UV is installed
Write-Host "[1/5] Checking UV installation..." -ForegroundColor Yellow
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "UV not found. Installing UV..." -ForegroundColor Yellow
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install UV!" -ForegroundColor Red
        exit 1
    }

    Write-Host "✓ UV installed successfully!" -ForegroundColor Green
} else {
    $uvVersion = uv --version
    Write-Host "✓ UV already installed: $uvVersion" -ForegroundColor Green
}

Write-Host ""

# Check Python version
Write-Host "[2/5] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green

Write-Host ""

# Sync dependencies
Write-Host "[3/5] Installing dependencies with UV..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes depending on your internet connection..." -ForegroundColor Gray
Write-Host ""

uv sync --extra client

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to sync dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "[4/5] Verifying installation..." -ForegroundColor Yellow

# Test PyTorch
Write-Host "  Testing PyTorch..." -ForegroundColor Gray
$torchTest = uv run python -c "import torch; print(f'PyTorch {torch.__version__} - CUDA: {torch.cuda.is_available()}')"
Write-Host "  ✓ $torchTest" -ForegroundColor Green

# Test Ollama
Write-Host "  Testing Ollama client..." -ForegroundColor Gray
uv run python -c "import ollama; print('Ollama client OK')" | Out-Null
Write-Host "  ✓ Ollama client OK" -ForegroundColor Green

# Test core imports
Write-Host "  Testing core packages..." -ForegroundColor Gray
uv run python -c "import pydantic, psutil, requests; print('Core packages OK')" | Out-Null
Write-Host "  ✓ Core packages OK" -ForegroundColor Green

Write-Host ""

# Show next steps
Write-Host "[5/5] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Activate the virtual environment:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Or run scripts directly with UV:" -ForegroundColor White
Write-Host "   uv run python VALCORE1\01_Client_Brain\main_client.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Read the UV guide:" -ForegroundColor White
Write-Host "   Get-Content UV_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Continue with Phase 2 setup:" -ForegroundColor White
Write-Host "   Get-Content VALCORE1\04_Documentation\00_READ_ME_FIRST.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ UV setup complete! Your development environment is ready." -ForegroundColor Green
Write-Host ""
