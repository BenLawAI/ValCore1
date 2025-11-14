#Requires -RunAsAdministrator

# VALCORE1 CUDA Test
# Tests CUDA installation and PyTorch GPU access

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 CUDA Test ===" -ForegroundColor Cyan
Write-Host "Testing CUDA installation and PyTorch GPU support`n"

$testsPassed = 0
$testsFailed = 0

# Test 1: Check CUDA installation
Write-Host "[Test 1/4] Checking CUDA installation..." -ForegroundColor Yellow

try {
    $cudaVersion = nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>$null

    if ($cudaVersion) {
        Write-Host "  PASS: CUDA driver found (version: $cudaVersion)" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "CUDA not detected"
    }
} catch {
    Write-Host "  FAIL: CUDA not found" -ForegroundColor Red
    Write-Host "  Fix: Install CUDA from https://developer.nvidia.com/cuda-downloads" -ForegroundColor Yellow
    $testsFailed++
}

# Test 2: Check PyTorch installation
Write-Host "`n[Test 2/4] Checking PyTorch installation..." -ForegroundColor Yellow

$pythonTest = @"
import sys
try:
    import torch
    print(f'INSTALLED:{torch.__version__}')
    sys.exit(0)
except ImportError:
    print('NOT_INSTALLED')
    sys.exit(1)
"@

try {
    $result = python -c $pythonTest 2>$null

    if ($result -like "INSTALLED:*") {
        $torchVersion = $result -replace "INSTALLED:", ""
        Write-Host "  PASS: PyTorch installed (version: $torchVersion)" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "PyTorch not installed"
    }
} catch {
    Write-Host "  FAIL: PyTorch not installed" -ForegroundColor Red
    Write-Host "  Fix: Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121" -ForegroundColor Yellow
    $testsFailed++
}

# Test 3: Check PyTorch CUDA availability
Write-Host "`n[Test 3/4] Checking PyTorch CUDA availability..." -ForegroundColor Yellow

$cudaTest = @"
import sys
try:
    import torch
    if torch.cuda.is_available():
        print(f'AVAILABLE:{torch.cuda.device_count()}')
        sys.exit(0)
    else:
        print('NOT_AVAILABLE')
        sys.exit(1)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

try {
    $result = python -c $cudaTest 2>$null

    if ($result -like "AVAILABLE:*") {
        $deviceCount = $result -replace "AVAILABLE:", ""
        Write-Host "  PASS: CUDA available in PyTorch ($deviceCount GPU(s) detected)" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "CUDA not available in PyTorch"
    }
} catch {
    Write-Host "  FAIL: CUDA not available in PyTorch" -ForegroundColor Red
    Write-Host "  Fix: Reinstall PyTorch with CUDA support" -ForegroundColor Yellow
    Write-Host "       pip uninstall torch torchvision torchaudio" -ForegroundColor Yellow
    Write-Host "       pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121" -ForegroundColor Yellow
    $testsFailed++
}

# Test 4: Test GPU computation
Write-Host "`n[Test 4/4] Testing GPU computation..." -ForegroundColor Yellow

$computeTest = @"
import sys
try:
    import torch
    if not torch.cuda.is_available():
        print('NO_CUDA')
        sys.exit(1)

    # Simple tensor operation on GPU
    device = torch.device('cuda:0')
    x = torch.randn(1000, 1000, device=device)
    y = torch.randn(1000, 1000, device=device)
    z = torch.matmul(x, y)

    print(f'SUCCESS:{device}')
    sys.exit(0)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

try {
    $result = python -c $computeTest 2>$null

    if ($result -like "SUCCESS:*") {
        Write-Host "  PASS: GPU computation successful" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "GPU computation failed"
    }
} catch {
    Write-Host "  FAIL: GPU computation failed" -ForegroundColor Red
    Write-Host "  Fix: Check CUDA installation and GPU drivers" -ForegroundColor Yellow
    $testsFailed++
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed/4" -ForegroundColor $(if ($testsPassed -eq 4) { "Green" } else { "Yellow" })
Write-Host "Tests Failed: $testsFailed/4" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`nCUDA Status: READY" -ForegroundColor Green
    Write-Host "Your system is ready for GPU-accelerated deep learning!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nCUDA Status: NOT READY" -ForegroundColor Red
    Write-Host "Please fix the issues above before running VALCORE1`n" -ForegroundColor Yellow
    exit 1
}
