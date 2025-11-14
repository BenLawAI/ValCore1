#Requires -RunAsAdministrator

# VALCORE1 Python Environment Test
# Tests Python installation and all required packages

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Python Environment Test ===" -ForegroundColor Cyan
Write-Host "Testing Python installation and dependencies`n"

$testsPassed = 0
$testsFailed = 0

# Test 1: Check Python version
Write-Host "[Test 1/6] Checking Python version..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1

    if ($pythonVersion -match "Python 3\.([0-9]+)\.([0-9]+)") {
        $minor = [int]$Matches[1]

        if ($minor -ge 10) {
            Write-Host "  PASS: $pythonVersion" -ForegroundColor Green
            $testsPassed++
        } else {
            throw "Python version too old: $pythonVersion"
        }
    } else {
        throw "Could not determine Python version"
    }
} catch {
    Write-Host "  FAIL: Python 3.10+ not found" -ForegroundColor Red
    Write-Host "  Fix: Install Python 3.10 or later from https://www.python.org/downloads/" -ForegroundColor Yellow
    $testsFailed++
}

# Test 2: Check pip
Write-Host "`n[Test 2/6] Checking pip..." -ForegroundColor Yellow

try {
    $pipVersion = pip --version 2>&1

    if ($pipVersion -match "pip") {
        Write-Host "  PASS: pip installed" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "pip not found"
    }
} catch {
    Write-Host "  FAIL: pip not found" -ForegroundColor Red
    Write-Host "  Fix: Install pip with: python -m ensurepip --upgrade" -ForegroundColor Yellow
    $testsFailed++
}

# Test 3: Check virtual environment
Write-Host "`n[Test 3/6] Checking virtual environment support..." -ForegroundColor Yellow

$venvTest = @"
import sys
import venv
print('VENV_OK')
"@

try {
    $result = python -c $venvTest 2>$null

    if ($result -eq "VENV_OK") {
        Write-Host "  PASS: venv module available" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "venv module not available"
    }
} catch {
    Write-Host "  FAIL: venv module not available" -ForegroundColor Red
    Write-Host "  Fix: Reinstall Python with venv support" -ForegroundColor Yellow
    $testsFailed++
}

# Test 4: Check critical packages
Write-Host "`n[Test 4/6] Checking critical packages..." -ForegroundColor Yellow

$requiredPackages = @(
    "torch",
    "faster-whisper",
    "sounddevice",
    "numpy",
    "requests",
    "pydantic",
    "flask",
    "pyautogui",
    "pystray",
    "pillow",
    "psutil",
    "pynvml"
)

$missingPackages = @()

foreach ($package in $requiredPackages) {
    $checkCmd = "import $($package.Replace('-', '_')); print('OK')"
    $result = python -c $checkCmd 2>$null

    if ($result -eq "OK") {
        Write-Host "  $package" -ForegroundColor Green -NoNewline
        Write-Host " - installed" -ForegroundColor Cyan
    } else {
        Write-Host "  $package" -ForegroundColor Red -NoNewline
        Write-Host " - MISSING" -ForegroundColor Red
        $missingPackages += $package
    }
}

if ($missingPackages.Count -eq 0) {
    Write-Host "`n  PASS: All critical packages installed" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "`n  FAIL: $($missingPackages.Count) package(s) missing" -ForegroundColor Red
    Write-Host "  Fix: Install missing packages:" -ForegroundColor Yellow
    Write-Host "       pip install $($missingPackages -join ' ')" -ForegroundColor Yellow
    $testsFailed++
}

# Test 5: Check optional packages
Write-Host "`n[Test 5/6] Checking optional packages..." -ForegroundColor Yellow

$optionalPackages = @(
    "faiss-cpu",
    "sentence-transformers",
    "pytesseract",
    "keyboard"
)

$missingOptional = @()

foreach ($package in $optionalPackages) {
    $checkCmd = "import $($package.Replace('-', '_')); print('OK')"
    $result = python -c $checkCmd 2>$null

    if ($result -eq "OK") {
        Write-Host "  $package" -ForegroundColor Green -NoNewline
        Write-Host " - installed" -ForegroundColor Cyan
    } else {
        Write-Host "  $package" -ForegroundColor Yellow -NoNewline
        Write-Host " - not installed (optional)" -ForegroundColor Yellow
        $missingOptional += $package
    }
}

if ($missingOptional.Count -eq 0) {
    Write-Host "`n  PASS: All optional packages installed" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "`n  INFO: Some optional packages not installed" -ForegroundColor Yellow
    Write-Host "  These packages are not required but provide enhanced functionality" -ForegroundColor Cyan
    Write-Host "  To install: pip install $($missingOptional -join ' ')" -ForegroundColor Cyan
    $testsPassed++
}

# Test 6: Check package versions compatibility
Write-Host "`n[Test 6/6] Checking package version compatibility..." -ForegroundColor Yellow

$compatTest = @"
import sys
try:
    import torch
    import numpy as np
    import pydantic

    # Test basic compatibility
    torch_version = torch.__version__
    numpy_version = np.__version__
    pydantic_version = pydantic.__version__

    print(f'torch:{torch_version}')
    print(f'numpy:{numpy_version}')
    print(f'pydantic:{pydantic_version}')

    # Try a simple operation
    x = torch.randn(10, 10)
    y = np.random.randn(10, 10)

    print('COMPAT_OK')
    sys.exit(0)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

try {
    $result = python -c $compatTest 2>&1

    if ($result -contains "COMPAT_OK") {
        Write-Host "  PASS: Package versions are compatible" -ForegroundColor Green

        # Display versions
        $versions = $result | Where-Object { $_ -match ":" -and $_ -notmatch "COMPAT_OK" }
        foreach ($version in $versions) {
            Write-Host "    $version" -ForegroundColor Cyan
        }

        $testsPassed++
    } else {
        throw "Compatibility test failed"
    }
} catch {
    Write-Host "  FAIL: Package version compatibility issues detected" -ForegroundColor Red
    Write-Host "  Fix: Update packages with: pip install --upgrade torch numpy pydantic" -ForegroundColor Yellow
    $testsFailed++
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed/6" -ForegroundColor $(if ($testsPassed -eq 6) { "Green" } else { "Yellow" })
Write-Host "Tests Failed: $testsFailed/6" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`nPython Environment Status: READY" -ForegroundColor Green
    Write-Host "Your Python environment is properly configured!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nPython Environment Status: NOT READY" -ForegroundColor Red
    Write-Host "Please fix the issues above before running VALCORE1`n" -ForegroundColor Yellow
    exit 1
}
