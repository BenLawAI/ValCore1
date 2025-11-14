# VALCORE1 GPU Detection Test
# For: Ben (non-programmer)
# Usage: Run in PowerShell as Administrator

Write-Host "`n=== VALCORE1 GPU Detection Test ===" -ForegroundColor Cyan
Write-Host "Checking NVIDIA GPUs and CUDA support...`n"

# Test 1: NVIDIA drivers
Write-Host "[1/4] Checking NVIDIA drivers..." -ForegroundColor Yellow

if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    Write-Host "✗ FAILED: nvidia-smi not found" -ForegroundColor Red
    Write-Host "`nFix: Install NVIDIA drivers from nvidia.com/Download" -ForegroundColor Yellow
    Write-Host "After install, restart PC and run this test again`n"
    exit 1
}

Write-Host "✓ NVIDIA drivers installed" -ForegroundColor Green

# Test 2: Detect GPUs
Write-Host "`n[2/4] Detecting GPUs..." -ForegroundColor Yellow

$gpuInfo = nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ FAILED: Could not detect GPUs" -ForegroundColor Red
    exit 1
}

$gpuCount = ($gpuInfo | Measure-Object).Count
Write-Host "✓ Found $gpuCount GPU(s):" -ForegroundColor Green

foreach ($gpu in $gpuInfo) {
    $parts = $gpu -split ','
    Write-Host "  GPU $($parts[0].Trim()): $($parts[1].Trim()) ($($parts[2].Trim()))" -ForegroundColor Cyan
}

$driverVersion = ($gpuInfo[0] -split ',')[3].Trim()
Write-Host "  Driver Version: $driverVersion" -ForegroundColor Cyan

# Test 3: CUDA availability
Write-Host "`n[3/4] Checking CUDA..." -ForegroundColor Yellow

$cudaTest = python -c "import torch; print(f'CUDA:{torch.cuda.is_available()}|Devices:{torch.cuda.device_count()}|Version:{torch.version.cuda}')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ FAILED: PyTorch not installed or CUDA unavailable" -ForegroundColor Red
    Write-Host "`nFix: Install CUDA Toolkit 12.1+ from developer.nvidia.com/cuda-downloads" -ForegroundColor Yellow
    Write-Host "Then: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`n"
    exit 1
}

$cudaParts = $cudaTest -split '\|'
$cudaAvailable = $cudaParts[0] -replace 'CUDA:', ''
$cudaDevices = $cudaParts[1] -replace 'Devices:', ''
$cudaVersion = $cudaParts[2] -replace 'Version:', ''

if ($cudaAvailable -eq 'True') {
    Write-Host "✓ CUDA Available: Yes" -ForegroundColor Green
    Write-Host "  CUDA Version: $cudaVersion" -ForegroundColor Cyan
    Write-Host "  PyTorch Detected Devices: $cudaDevices" -ForegroundColor Cyan
} else {
    Write-Host "✗ FAILED: CUDA not available to PyTorch" -ForegroundColor Red
    exit 1
}

# Test 4: Verify expected GPUs
Write-Host "`n[4/4] Verifying GPU configuration..." -ForegroundColor Yellow

$expectedGPUs = @("RTX 5070", "RTX 4070")
$detectedGPUNames = $gpuInfo | ForEach-Object { ($_ -split ',')[1].Trim() }

$allFound = $true
foreach ($expected in $expectedGPUs) {
    $found = $detectedGPUNames | Where-Object { $_ -like "*$expected*" }
    if ($found) {
        Write-Host "✓ Found expected GPU: $expected" -ForegroundColor Green
    } else {
        Write-Host "✗ Expected GPU not found: $expected" -ForegroundColor Red
        $allFound = $false
    }
}

# Final result
Write-Host "`n=== TEST RESULT ===" -ForegroundColor Cyan

if ($allFound) {
    Write-Host "✓ ALL CHECKS PASSED" -ForegroundColor Green
    Write-Host "`nCopy ALL the output above and send to Val" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✗ SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "Copy ALL the output above and send to Val for troubleshooting" -ForegroundColor Yellow
    exit 1
}
