#Requires -RunAsAdministrator

# VALCORE1 Tailscale Setup (Windows Client)
# Sets up Tailscale for remote access to ATOM server

param(
    [switch]$Silent
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Tailscale Setup (Windows) ===" -ForegroundColor Cyan
Write-Host "This script will install and configure Tailscale for remote ATOM access`n"

if (-not $Silent) {
    $confirm = Read-Host "Continue? (Y/N)"
    if ($confirm -ne 'Y') {
        Write-Host "Cancelled." -ForegroundColor Red
        exit 1
    }
}

# 1. Install Tailscale
Write-Host "`n[1/4] Installing Tailscale..." -ForegroundColor Yellow

# Check if already installed
$tailscaleInstalled = Get-Command tailscale -ErrorAction SilentlyContinue

if ($tailscaleInstalled) {
    Write-Host "  ✓ Tailscale already installed" -ForegroundColor Green
} else {
    Write-Host "  Installing via winget..." -ForegroundColor Cyan

    try {
        winget install tailscale.tailscale --silent --accept-source-agreements --accept-package-agreements

        if ($LASTEXITCODE -ne 0) {
            throw "winget install failed"
        }

        Write-Host "  ✓ Tailscale installed" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Installation failed" -ForegroundColor Red
        Write-Host "  Manual install: Download from https://tailscale.com/download/windows" -ForegroundColor Yellow
        exit 1
    }
}

# 2. Login to Tailscale
Write-Host "`n[2/4] Logging in to Tailscale..." -ForegroundColor Yellow
Write-Host "  A browser window will open for authentication" -ForegroundColor Cyan
Write-Host "  Please log in and authorize this device`n" -ForegroundColor Cyan

Start-Sleep -Seconds 2

try {
    tailscale login

    if ($LASTEXITCODE -ne 0) {
        throw "Tailscale login failed"
    }

    Write-Host "  ✓ Logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Login failed" -ForegroundColor Red
    Write-Host "  Please run manually: tailscale login" -ForegroundColor Yellow
    exit 1
}

# 3. Wait for connection
Write-Host "`n[3/4] Waiting for Tailscale connection..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$status = tailscale status --json | ConvertFrom-Json

if ($status.BackendState -eq "Running") {
    Write-Host "  ✓ Tailscale connected" -ForegroundColor Green
    Write-Host "  Your Tailscale IP: $($status.Self.TailscaleIPs[0])" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠ Tailscale state: $($status.BackendState)" -ForegroundColor Yellow
}

# 4. Configure ATOM connection
Write-Host "`n[4/4] Configuring ATOM connection..." -ForegroundColor Yellow

$atomIP = Read-Host "Enter ATOM's Tailscale IP (format: 100.x.x.x)"

# Validate IP format
if ($atomIP -notmatch '^100\.\d+\.\d+\.\d+$') {
    Write-Host "  ⚠ Invalid Tailscale IP format" -ForegroundColor Yellow
    Write-Host "  Expected format: 100.x.x.x" -ForegroundColor Yellow
    Write-Host "  Continuing anyway..." -ForegroundColor Yellow
}

# Update network config
$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json"

if (Test-Path $configPath) {
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        $config.atom_tailscale_ip = $atomIP
        $config.prefer_tailscale = $true
        $config | ConvertTo-Json -Depth 10 | Set-Content $configPath

        Write-Host "  ✓ Network config updated" -ForegroundColor Green
        Write-Host "    Tailscale IP: $atomIP" -ForegroundColor Cyan
        Write-Host "    Prefer Tailscale: enabled" -ForegroundColor Cyan
    } catch {
        Write-Host "  ✗ Failed to update config: $_" -ForegroundColor Red
        Write-Host "  Manual update required: $configPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Config file not found: $configPath" -ForegroundColor Yellow
    Write-Host "  You'll need to update this manually later" -ForegroundColor Yellow
}

# Final status
Write-Host "`n=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host "`nTailscale Configuration:" -ForegroundColor Cyan
Write-Host "  Your Tailscale IP: $($status.Self.TailscaleIPs[0])" -ForegroundColor White
Write-Host "  ATOM IP: $atomIP" -ForegroundColor White
Write-Host "  Connection: Ready for remote access`n" -ForegroundColor White

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify ATOM is also connected to Tailscale" -ForegroundColor White
Write-Host "  2. Test connection: ping $atomIP" -ForegroundColor White
Write-Host "  3. Test VALCORE1 with remote access`n" -ForegroundColor White
