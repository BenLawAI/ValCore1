<#
.SYNOPSIS
    Quick dependency check for VALCORE1 (no downloads)

.DESCRIPTION
    Quickly checks what dependencies are installed without downloading anything.
    Useful for troubleshooting and verifying setup.

.EXAMPLE
    .\check_dependencies.ps1
#>

param(
    [switch]$Verbose,
    [switch]$ExportReport
)

# Colors
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

function Test-Dependency {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$SuccessMessage = "",
        [string]$FailureMessage = ""
    )

    Write-Host -NoNewline "$Name... " -ForegroundColor $ColorInfo

    try {
        $result = & $Test
        if ($result) {
            Write-Host "[OK]" -ForegroundColor $ColorSuccess
            if ($Verbose -and $SuccessMessage) {
                Write-Host "  $SuccessMessage" -ForegroundColor $ColorSuccess
            }
            return $true
        }
        else {
            Write-Host "[MISSING]" -ForegroundColor $ColorError
            if ($FailureMessage) {
                Write-Host "  $FailureMessage" -ForegroundColor $ColorWarning
            }
            return $false
        }
    }
    catch {
        Write-Host "[ERROR]" -ForegroundColor $ColorError
        if ($Verbose) {
            Write-Host "  $_" -ForegroundColor $ColorError
        }
        return $false
    }
}

Write-Host @"

VALCORE1 Dependency Check
========================

"@ -ForegroundColor Cyan

# System checks
Write-Host "`n[SYSTEM]" -ForegroundColor Magenta

$checks = @{
    Passed = 0
    Failed = 0
}

# PowerShell version
if (Test-Dependency "PowerShell 5.1+" {
    return $PSVersionTable.PSVersion.Major -ge 5
} -SuccessMessage "Version $($PSVersionTable.PSVersion)") {
    $checks.Passed++
} else {
    $checks.Failed++
}

# Python
Write-Host "`n[PYTHON]" -ForegroundColor Magenta

if (Test-Dependency "Python 3.10+" {
    try {
        $version = & python --version 2>&1
        if ($version -match "Python (\d+\.\d+)") {
            $pyVer = [Version]$matches[1]
            return $pyVer.Major -eq 3 -and $pyVer.Minor -ge 10
        }
        return $false
    } catch { return $false }
} -SuccessMessage (& python --version 2>&1) -FailureMessage "Install Python 3.10+ from python.org") {
    $checks.Passed++
} else {
    $checks.Failed++
}

if (Test-Dependency "pip" {
    try {
        $null = & pip --version 2>&1
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}) {
    $checks.Passed++
} else {
    $checks.Failed++
}

# NVIDIA/CUDA
Write-Host "`n[NVIDIA/CUDA]" -ForegroundColor Magenta

if (Test-Dependency "nvidia-smi" {
    try {
        $null = & nvidia-smi 2>&1
        return $LASTEXITCODE -eq 0
    } catch { return $false }
} -FailureMessage "Install NVIDIA drivers from nvidia.com") {
    $checks.Passed++

    # Show GPU info if verbose
    if ($Verbose) {
        Write-Host "`n  GPUs detected:" -ForegroundColor $ColorInfo
        & nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader 2>&1 | ForEach-Object {
            Write-Host "    $_" -ForegroundColor $ColorInfo
        }
    }
} else {
    $checks.Failed++
}

# PyTorch
Write-Host "`n[PYTORCH]" -ForegroundColor Magenta

if (Test-Dependency "PyTorch" {
    try {
        $null = & python -c "import torch" 2>&1
        return $LASTEXITCODE -eq 0
    } catch { return $false }
} -FailureMessage "Install with: pip install torch --index-url https://download.pytorch.org/whl/cu121") {
    $checks.Passed++

    if (Test-Dependency "PyTorch CUDA" {
        $result = & python -c "import torch; print(torch.cuda.is_available())" 2>&1
        return $result -eq "True"
    } -SuccessMessage "CUDA support enabled") {
        $checks.Passed++
    } else {
        $checks.Failed++
    }

    if (Test-Dependency "GPU Count" {
        $count = & python -c "import torch; print(torch.cuda.device_count())" 2>&1
        return [int]$count -gt 0
    } -SuccessMessage "$(& python -c "import torch; print(torch.cuda.device_count())" 2>&1) GPU(s) available") {
        $checks.Passed++
    } else {
        $checks.Failed++
    }
} else {
    $checks.Failed++
}

# Core Dependencies
Write-Host "`n[CORE DEPENDENCIES]" -ForegroundColor Magenta

$coreDeps = @(
    @{ Name = "faster-whisper"; ImportTest = "from faster_whisper import WhisperModel" }
    @{ Name = "pyaudio"; ImportTest = "import pyaudio" }
    @{ Name = "sounddevice"; ImportTest = "import sounddevice" }
    @{ Name = "pvporcupine"; ImportTest = "import pvporcupine" }
    @{ Name = "numpy"; ImportTest = "import numpy" }
    @{ Name = "requests"; ImportTest = "import requests" }
    @{ Name = "flask"; ImportTest = "import flask" }
)

foreach ($dep in $coreDeps) {
    if (Test-Dependency $dep.Name {
        try {
            $null = & python -c $dep.ImportTest 2>&1
            return $LASTEXITCODE -eq 0
        } catch { return $false }
    }) {
        $checks.Passed++
    } else {
        $checks.Failed++
    }
}

# Automation
Write-Host "`n[AUTOMATION]" -ForegroundColor Magenta

$automationDeps = @("pyautogui", "pygetwindow", "pytesseract")

foreach ($dep in $automationDeps) {
    if (Test-Dependency $dep {
        try {
            $null = & python -c "import $dep" 2>&1
            return $LASTEXITCODE -eq 0
        } catch { return $false }
    }) {
        $checks.Passed++
    } else {
        $checks.Failed++
    }
}

# Optional (Server)
Write-Host "`n[SERVER DEPENDENCIES (Optional)]" -ForegroundColor Magenta

$serverDeps = @(
    "ollama",
    "faiss",
    "sentence-transformers",
    "schedule"
)

foreach ($dep in $serverDeps) {
    $depModule = $dep -replace '-', '_'
    if (Test-Dependency $dep {
        try {
            $null = & python -c "import $depModule" 2>&1
            return $LASTEXITCODE -eq 0
        } catch { return $false }
    }) {
        $checks.Passed++
    } else {
        Write-Host "  (Optional - not critical)" -ForegroundColor $ColorWarning
    }
}

# Summary
Write-Host "`n" + ("=" * 80) -ForegroundColor Magenta
Write-Host "SUMMARY" -ForegroundColor Magenta
Write-Host ("=" * 80) -ForegroundColor Magenta

$total = $checks.Passed + $checks.Failed
$percentage = [math]::Round(($checks.Passed / $total) * 100, 1)

Write-Host "`nTests Passed: " -NoNewline -ForegroundColor $ColorInfo
Write-Host "$($checks.Passed)/$total " -NoNewline -ForegroundColor $(if ($checks.Failed -eq 0) { $ColorSuccess } else { $ColorWarning })
Write-Host "($percentage%)" -ForegroundColor $(if ($checks.Failed -eq 0) { $ColorSuccess } else { $ColorWarning })

if ($checks.Failed -eq 0) {
    Write-Host "`n✓ All dependencies satisfied!" -ForegroundColor $ColorSuccess
    Write-Host "Ready to run VALCORE1" -ForegroundColor $ColorSuccess
}
elseif ($checks.Failed -le 3) {
    Write-Host "`n⚠ Some dependencies missing" -ForegroundColor $ColorWarning
    Write-Host "Run: .\download_dependencies.ps1" -ForegroundColor $ColorInfo
}
else {
    Write-Host "`n✗ Many dependencies missing" -ForegroundColor $ColorError
    Write-Host "Run: .\download_dependencies.ps1" -ForegroundColor $ColorInfo
}

Write-Host ""

# Export report if requested
if ($ExportReport) {
    $reportPath = "dependency_check_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

    @"
VALCORE1 Dependency Check Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Summary:
--------
Passed: $($checks.Passed)/$total ($percentage%)
Failed: $($checks.Failed)

System:
-------
PowerShell: $($PSVersionTable.PSVersion)
Python: $(& python --version 2>&1)
OS: $([System.Environment]::OSVersion.VersionString)

GPU:
----
$(& nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv 2>&1)

PyTorch:
--------
$(& python -c "import torch; print(f'Version: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPUs: {torch.cuda.device_count()}')" 2>&1)

Installed Packages:
-------------------
$(& pip list 2>&1)
"@ | Out-File -FilePath $reportPath -Encoding utf8

    Write-Host "Report exported to: $reportPath" -ForegroundColor $ColorSuccess
}
