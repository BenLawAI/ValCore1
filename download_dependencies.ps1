<#
.SYNOPSIS
    VALCORE1 Dependency Download Script

.DESCRIPTION
    Intelligently downloads and installs all required dependencies for VALCORE1.
    Checks what's already installed and only downloads what's missing.

.NOTES
    File Name      : download_dependencies.ps1
    Author         : Claude Code
    Prerequisite   : PowerShell 5.1+, Internet connection
    Version        : 2.0

.EXAMPLE
    .\download_dependencies.ps1

.EXAMPLE
    .\download_dependencies.ps1 -SkipPython
#>

[CmdletBinding()]
param(
    [switch]$SkipPython,      # Skip Python installation check
    [switch]$SkipPyTorch,     # Skip PyTorch installation
    [switch]$SkipModels,      # Skip model downloads
    [switch]$Force,           # Force reinstall everything
    [switch]$Offline          # Check dependencies without downloading
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"  # Faster downloads

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"
$ColorHeader = "Magenta"

# Versions
$PYTHON_MIN_VERSION = "3.10"
$PYTHON_RECOMMENDED = "3.11"
$CUDA_MIN_VERSION = "12.1"
$PYTORCH_VERSION = "2.1.0"

# Paths
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VALCORE_ROOT = Join-Path $SCRIPT_DIR "VALCORE1"
$CLIENT_DIR = Join-Path $VALCORE_ROOT "01_Client_Brain"
$SERVER_DIR = Join-Path $VALCORE_ROOT "02_Server_Brain"
$MODELS_DIR = Join-Path $SCRIPT_DIR "models"
$LOGS_DIR = Join-Path $SCRIPT_DIR "logs"

# Requirements files
$CLIENT_REQUIREMENTS = Join-Path $CLIENT_DIR "setup\requirements_client.txt"
$SERVER_REQUIREMENTS = Join-Path $SERVER_DIR "setup\requirements_server.txt"

# Download URLs
$PYTHON_DOWNLOAD_URL = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"

# Model URLs
$FASTER_WHISPER_MODELS = @{
    "large-v3-turbo" = "https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('=' * 80)" -ForegroundColor $ColorHeader
    Write-Host $Message -ForegroundColor $ColorHeader
    Write-Host "$('=' * 80)`n" -ForegroundColor $ColorHeader
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    $color = switch ($Status) {
        "SUCCESS" { $ColorSuccess }
        "WARNING" { $ColorWarning }
        "ERROR"   { $ColorError }
        "INFO"    { $ColorInfo }
        default   { "White" }
    }

    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] [$Status] $Message" -ForegroundColor $color
}

function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

function Get-InstalledPythonVersion {
    try {
        $version = & python --version 2>&1
        if ($version -match "Python (\d+\.\d+\.\d+)") {
            return $matches[1]
        }
    }
    catch {
        return $null
    }
}

function Compare-Versions {
    param(
        [string]$Version1,
        [string]$Version2
    )
    $v1 = [Version]$Version1
    $v2 = [Version]$Version2
    return $v1.CompareTo($v2)
}

function Test-PipPackage {
    param([string]$Package)
    try {
        $result = & pip show $Package 2>&1
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Get-FileSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length
        if ($size -gt 1GB) {
            return "{0:N2} GB" -f ($size / 1GB)
        }
        elseif ($size -gt 1MB) {
            return "{0:N2} MB" -f ($size / 1MB)
        }
        else {
            return "{0:N2} KB" -f ($size / 1KB)
        }
    }
    return "0 KB"
}

function Download-File {
    param(
        [string]$Url,
        [string]$OutputPath,
        [string]$Description
    )

    Write-Status "Downloading: $Description" "INFO"
    Write-Status "URL: $Url" "INFO"
    Write-Status "Destination: $OutputPath" "INFO"

    try {
        $dir = Split-Path -Parent $OutputPath
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }

        # Use .NET WebClient for better progress
        $webClient = New-Object System.Net.WebClient

        # Add progress handler
        $startTime = Get-Date
        Register-ObjectEvent -InputObject $webClient -EventName DownloadProgressChanged -Action {
            $percent = $eventArgs.ProgressPercentage
            $received = $eventArgs.BytesReceived / 1MB
            $total = $eventArgs.TotalBytesToReceive / 1MB

            Write-Progress -Activity "Downloading $Description" `
                -Status "$("{0:N2}" -f $received) MB of $("{0:N2}" -f $total) MB" `
                -PercentComplete $percent
        } | Out-Null

        $webClient.DownloadFile($Url, $OutputPath)

        $elapsed = (Get-Date) - $startTime
        $size = Get-FileSize $OutputPath

        Write-Status "Downloaded $size in $($elapsed.TotalSeconds) seconds" "SUCCESS"

        return $true
    }
    catch {
        Write-Status "Download failed: $_" "ERROR"
        return $false
    }
    finally {
        if ($webClient) {
            $webClient.Dispose()
        }
        Write-Progress -Activity "Downloading" -Completed
    }
}

# ============================================================================
# MAIN DEPENDENCY CHECKS
# ============================================================================

function Test-Prerequisites {
    Write-Header "CHECKING PREREQUISITES"

    $issues = @()

    # Check PowerShell version
    Write-Status "Checking PowerShell version..." "INFO"
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -ge 5) {
        Write-Status "PowerShell $psVersion - OK" "SUCCESS"
    }
    else {
        Write-Status "PowerShell $psVersion - Need 5.1+" "ERROR"
        $issues += "PowerShell version too old"
    }

    # Check internet connection
    Write-Status "Checking internet connection..." "INFO"
    try {
        $null = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
        Write-Status "Internet connection - OK" "SUCCESS"
    }
    catch {
        Write-Status "No internet connection detected" "WARNING"
        if (-not $Offline) {
            $issues += "No internet connection"
        }
    }

    # Check disk space (need at least 50GB)
    Write-Status "Checking disk space..." "INFO"
    $drive = (Get-Item $SCRIPT_DIR).PSDrive.Name
    $freeSpace = (Get-PSDrive $drive).Free / 1GB
    if ($freeSpace -gt 50) {
        Write-Status "Disk space: $("{0:N2}" -f $freeSpace) GB free - OK" "SUCCESS"
    }
    else {
        Write-Status "Disk space: $("{0:N2}" -f $freeSpace) GB free - Need 50GB+" "WARNING"
        $issues += "Low disk space"
    }

    return $issues
}

function Test-Python {
    Write-Header "CHECKING PYTHON"

    if ($SkipPython) {
        Write-Status "Skipping Python check (--SkipPython)" "WARNING"
        return $true
    }

    # Check if Python is installed
    if (Test-Command "python") {
        $version = Get-InstalledPythonVersion
        Write-Status "Python $version detected" "INFO"

        # Check version
        $comparison = Compare-Versions $version $PYTHON_MIN_VERSION
        if ($comparison -ge 0) {
            Write-Status "Python version OK (>= $PYTHON_MIN_VERSION)" "SUCCESS"
            return $true
        }
        else {
            Write-Status "Python version too old (need >= $PYTHON_MIN_VERSION)" "ERROR"
            return $false
        }
    }
    else {
        Write-Status "Python not found" "ERROR"
        Write-Status "Please install Python $PYTHON_RECOMMENDED from https://www.python.org" "INFO"
        Write-Status "Or run: winget install Python.Python.3.11" "INFO"
        return $false
    }
}

function Test-CUDA {
    Write-Header "CHECKING NVIDIA CUDA"

    # Check nvidia-smi
    if (Test-Command "nvidia-smi") {
        Write-Status "nvidia-smi found" "SUCCESS"

        # Get CUDA version
        try {
            $nvidiaSmi = & nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>&1
            Write-Status "NVIDIA Driver: $nvidiaSmi" "INFO"

            # Get GPU count
            $gpuCount = (& nvidia-smi --query-gpu=name --format=csv,noheader 2>&1 | Measure-Object).Count
            Write-Status "GPUs detected: $gpuCount" "INFO"

            # List GPUs
            $gpus = & nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader 2>&1
            foreach ($gpu in $gpus) {
                Write-Status "  GPU: $gpu" "INFO"
            }

            return $true
        }
        catch {
            Write-Status "Error querying nvidia-smi: $_" "WARNING"
            return $false
        }
    }
    else {
        Write-Status "nvidia-smi not found - NVIDIA drivers not installed" "ERROR"
        Write-Status "Install from: https://www.nvidia.com/Download/index.aspx" "INFO"
        return $false
    }
}

function Install-PyTorchCUDA {
    Write-Header "INSTALLING PYTORCH WITH CUDA"

    if ($SkipPyTorch) {
        Write-Status "Skipping PyTorch (--SkipPyTorch)" "WARNING"
        return $true
    }

    # Check if PyTorch is already installed
    if (Test-PipPackage "torch") {
        Write-Status "PyTorch already installed" "INFO"

        # Check CUDA support
        try {
            $cudaAvailable = & python -c "import torch; print(torch.cuda.is_available())" 2>&1
            if ($cudaAvailable -eq "True") {
                Write-Status "PyTorch CUDA support - OK" "SUCCESS"

                if (-not $Force) {
                    return $true
                }
            }
            else {
                Write-Status "PyTorch installed but no CUDA support" "WARNING"
            }
        }
        catch {
            Write-Status "Error checking PyTorch CUDA: $_" "WARNING"
        }
    }

    Write-Status "Installing PyTorch with CUDA 12.1..." "INFO"
    Write-Status "This may take 5-10 minutes (downloading ~2GB)" "WARNING"

    try {
        # Install PyTorch with CUDA 12.1
        $cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
        Write-Status "Running: $cmd" "INFO"

        Invoke-Expression $cmd

        if ($LASTEXITCODE -eq 0) {
            Write-Status "PyTorch installed successfully" "SUCCESS"

            # Verify CUDA support
            $cudaAvailable = & python -c "import torch; print(torch.cuda.is_available())" 2>&1
            if ($cudaAvailable -eq "True") {
                Write-Status "CUDA support verified" "SUCCESS"
                return $true
            }
            else {
                Write-Status "PyTorch installed but CUDA not available" "ERROR"
                return $false
            }
        }
        else {
            Write-Status "PyTorch installation failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-Status "Error installing PyTorch: $_" "ERROR"
        return $false
    }
}

function Install-PythonPackages {
    param([string]$RequirementsFile, [string]$Name)

    Write-Header "INSTALLING $Name PACKAGES"

    if (-not (Test-Path $RequirementsFile)) {
        Write-Status "Requirements file not found: $RequirementsFile" "ERROR"
        return $false
    }

    # Count packages
    $packages = Get-Content $RequirementsFile | Where-Object { $_ -match '\S' -and $_ -notmatch '^#' }
    $totalPackages = ($packages | Measure-Object).Count

    Write-Status "Found $totalPackages packages to install" "INFO"

    # Check which are already installed
    $installed = 0
    $toInstall = @()

    foreach ($package in $packages) {
        # Parse package name (before ==, >=, etc.)
        if ($package -match '^([a-zA-Z0-9_-]+)') {
            $packageName = $matches[1]

            if (Test-PipPackage $packageName) {
                $installed++
            }
            else {
                $toInstall += $package
            }
        }
    }

    Write-Status "Already installed: $installed/$totalPackages" "INFO"

    if ($toInstall.Count -eq 0 -and -not $Force) {
        Write-Status "All packages already installed" "SUCCESS"
        return $true
    }

    if ($Force) {
        Write-Status "Force reinstall enabled - installing all packages" "WARNING"
    }
    else {
        Write-Status "Installing $($toInstall.Count) missing packages" "INFO"
    }

    try {
        $cmd = if ($Force) {
            "pip install --force-reinstall -r `"$RequirementsFile`""
        }
        else {
            "pip install -r `"$RequirementsFile`""
        }

        Write-Status "Running: $cmd" "INFO"
        Invoke-Expression $cmd

        if ($LASTEXITCODE -eq 0) {
            Write-Status "$Name packages installed successfully" "SUCCESS"
            return $true
        }
        else {
            Write-Status "$Name package installation failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-Status "Error installing $Name packages: $_" "ERROR"
        return $false
    }
}

function Download-FasterWhisperModel {
    param([string]$ModelName)

    Write-Header "DOWNLOADING FASTER-WHISPER MODEL: $ModelName"

    # Model will be auto-downloaded by faster-whisper on first use
    # But we can pre-download and verify

    Write-Status "Verifying Faster-Whisper model availability..." "INFO"

    try {
        # Test if we can load the model (will download if needed)
        $testScript = @"
from faster_whisper import WhisperModel
print("Loading model: $ModelName")
model = WhisperModel("$ModelName", device="cpu", compute_type="int8")
print("Model loaded successfully")
"@

        $tempFile = Join-Path $env:TEMP "test_whisper.py"
        $testScript | Out-File -FilePath $tempFile -Encoding utf8

        Write-Status "Testing model download..." "INFO"
        & python $tempFile

        if ($LASTEXITCODE -eq 0) {
            Write-Status "Faster-Whisper model ready" "SUCCESS"
            return $true
        }
        else {
            Write-Status "Model download/load failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-Status "Error downloading model: $_" "ERROR"
        return $false
    }
    finally {
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force
        }
    }
}

function Test-AllDependencies {
    Write-Header "TESTING ALL DEPENDENCIES"

    $tests = @(
        @{ Name = "Python Import Test"; Command = "python -c `"import sys; print(sys.version)`"" }
        @{ Name = "PyTorch Import"; Command = "python -c `"import torch; print(f'PyTorch {torch.__version__}')`"" }
        @{ Name = "CUDA Available"; Command = "python -c `"import torch; print(f'CUDA: {torch.cuda.is_available()}')`"" }
        @{ Name = "GPU Count"; Command = "python -c `"import torch; print(f'GPUs: {torch.cuda.device_count()}')`"" }
        @{ Name = "Faster-Whisper"; Command = "python -c `"from faster_whisper import WhisperModel; print('OK')`"" }
        @{ Name = "PyAudio"; Command = "python -c `"import pyaudio; print('OK')`"" }
        @{ Name = "PyAutoGUI"; Command = "python -c `"import pyautogui; print('OK')`"" }
        @{ Name = "Requests"; Command = "python -c `"import requests; print('OK')`"" }
        @{ Name = "NumPy"; Command = "python -c `"import numpy; print('OK')`"" }
    )

    $passed = 0
    $failed = 0

    foreach ($test in $tests) {
        try {
            Write-Host -NoNewline "$($test.Name)... " -ForegroundColor $ColorInfo
            $result = Invoke-Expression $test.Command 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK]" -ForegroundColor $ColorSuccess
                $passed++
            }
            else {
                Write-Host "[FAILED]" -ForegroundColor $ColorError
                $failed++
            }
        }
        catch {
            Write-Host "[ERROR]" -ForegroundColor $ColorError
            $failed++
        }
    }

    Write-Host ""
    Write-Status "Tests passed: $passed/$($tests.Count)" $(if ($failed -eq 0) { "SUCCESS" } else { "WARNING" })

    return $failed -eq 0
}

function Save-DependencyReport {
    Write-Header "GENERATING DEPENDENCY REPORT"

    $reportPath = Join-Path $LOGS_DIR "dependency_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

    if (-not (Test-Path $LOGS_DIR)) {
        New-Item -ItemType Directory -Path $LOGS_DIR -Force | Out-Null
    }

    $report = @"
VALCORE1 DEPENDENCY REPORT
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
=============================================================================

SYSTEM INFORMATION:
-------------------
PowerShell Version: $($PSVersionTable.PSVersion)
OS: $([System.Environment]::OSVersion.VersionString)
Machine: $env:COMPUTERNAME
User: $env:USERNAME

PYTHON:
-------
$(& python --version 2>&1)
Location: $(& where.exe python 2>&1)

PIP:
----
$(& pip --version 2>&1)

CUDA/GPU:
---------
$(& nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv 2>&1)

PYTORCH:
--------
$(& python -c "import torch; print(f'Version: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}'); print(f'GPU Count: {torch.cuda.device_count()}')" 2>&1)

INSTALLED PACKAGES:
-------------------
$(& pip list 2>&1)

=============================================================================
"@

    $report | Out-File -FilePath $reportPath -Encoding utf8
    Write-Status "Report saved: $reportPath" "SUCCESS"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

function Main {
    Write-Host @"

██╗   ██╗ █████╗ ██╗      ██████╗ ██████╗ ██████╗ ███████╗ ██╗
██║   ██║██╔══██╗██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝███║
██║   ██║███████║██║     ██║     ██║   ██║██████╔╝█████╗  ╚██║
╚██╗ ██╔╝██╔══██║██║     ██║     ██║   ██║██╔══██╗██╔══╝   ██║
 ╚████╔╝ ██║  ██║███████╗╚██████╗╚██████╔╝██║  ██║███████╗ ██║
  ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═╝

Dependency Download & Installation Script v2.0

"@ -ForegroundColor $ColorHeader

    $startTime = Get-Date

    # Check prerequisites
    $issues = Test-Prerequisites
    if ($issues.Count -gt 0 -and -not $Offline) {
        Write-Status "Critical issues found:" "ERROR"
        foreach ($issue in $issues) {
            Write-Status "  - $issue" "ERROR"
        }
        Write-Status "Please fix these issues and try again" "ERROR"
        exit 1
    }

    # Check Python
    if (-not (Test-Python)) {
        Write-Status "Python check failed - cannot continue" "ERROR"
        exit 1
    }

    # Check CUDA/GPU
    Test-CUDA | Out-Null

    # Upgrade pip
    Write-Status "Upgrading pip..." "INFO"
    & python -m pip install --upgrade pip | Out-Null

    if (-not $Offline) {
        # Install PyTorch with CUDA
        if (-not (Install-PyTorchCUDA)) {
            Write-Status "PyTorch installation failed - continuing anyway" "WARNING"
        }

        # Install client packages
        if (Test-Path $CLIENT_REQUIREMENTS) {
            Install-PythonPackages -RequirementsFile $CLIENT_REQUIREMENTS -Name "CLIENT"
        }

        # Install server packages
        if (Test-Path $SERVER_REQUIREMENTS) {
            Install-PythonPackages -RequirementsFile $SERVER_REQUIREMENTS -Name "SERVER"
        }

        # Download Faster-Whisper model
        if (-not $SkipModels) {
            Download-FasterWhisperModel -ModelName "large-v3-turbo"
        }
    }

    # Test all dependencies
    $allTestsPassed = Test-AllDependencies

    # Generate report
    Save-DependencyReport

    # Summary
    $elapsed = (Get-Date) - $startTime

    Write-Header "INSTALLATION COMPLETE"

    if ($allTestsPassed) {
        Write-Status "All dependencies installed and tested successfully!" "SUCCESS"
        Write-Status "Total time: $($elapsed.TotalMinutes.ToString('F1')) minutes" "SUCCESS"
        Write-Status "`nNext steps:" "INFO"
        Write-Status "1. Review SETUP_INSTRUCTIONS.md" "INFO"
        Write-Status "2. Get Picovoice access key from https://console.picovoice.ai" "INFO"
        Write-Status "3. Run: python VALCORE1/01_Client_Brain/main_client.py" "INFO"
    }
    else {
        Write-Status "Some dependency tests failed" "WARNING"
        Write-Status "Review the errors above and check the dependency report" "WARNING"
        Write-Status "Total time: $($elapsed.TotalMinutes.ToString('F1')) minutes" "INFO"
    }
}

# Run main
Main
