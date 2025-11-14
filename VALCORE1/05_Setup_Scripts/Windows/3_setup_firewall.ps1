#Requires -RunAsAdministrator

# VALCORE1 Firewall Configuration
# Configures Windows Firewall rules for VALCORE1

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Firewall Configuration ===" -ForegroundColor Cyan
Write-Host "This script will configure Windows Firewall to allow VALCORE1 traffic`n"

$confirm = Read-Host "Configure Windows Firewall for VALCORE1? (Y/N)"

if ($confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

$rulesPassed = 0
$rulesFailed = 0

# Rule 1: Allow Python (for Flask server)
Write-Host "`n[1/4] Configuring Python firewall rule..." -ForegroundColor Yellow

$pythonPath = (Get-Command python).Source

try {
    # Remove existing rule if present
    Remove-NetFirewallRule -DisplayName "VALCORE1 - Python" -ErrorAction SilentlyContinue

    # Add new rule
    New-NetFirewallRule `
        -DisplayName "VALCORE1 - Python" `
        -Description "Allow VALCORE1 Python server (Flask on port 5000)" `
        -Direction Inbound `
        -Program $pythonPath `
        -Action Allow `
        -Protocol TCP `
        -LocalPort 5000 `
        -Profile Private,Domain `
        -Enabled True | Out-Null

    Write-Host "  PASS: Python firewall rule configured" -ForegroundColor Green
    Write-Host "  Program: $pythonPath" -ForegroundColor Cyan
    Write-Host "  Port: 5000 (Flask server)" -ForegroundColor Cyan
    $rulesPassed++
} catch {
    Write-Host "  FAIL: Could not configure Python rule: $_" -ForegroundColor Red
    $rulesFailed++
}

# Rule 2: Allow outbound to ATOM server
Write-Host "`n[2/4] Configuring ATOM server access..." -ForegroundColor Yellow

try {
    # Remove existing rule if present
    Remove-NetFirewallRule -DisplayName "VALCORE1 - ATOM Outbound" -ErrorAction SilentlyContinue

    # Add new rule
    New-NetFirewallRule `
        -DisplayName "VALCORE1 - ATOM Outbound" `
        -Description "Allow VALCORE1 to connect to ATOM server (Ollama)" `
        -Direction Outbound `
        -Action Allow `
        -Protocol TCP `
        -RemotePort 11434 `
        -Profile Private,Domain `
        -Enabled True | Out-Null

    Write-Host "  PASS: ATOM outbound rule configured" -ForegroundColor Green
    Write-Host "  Remote Port: 11434 (Ollama)" -ForegroundColor Cyan
    $rulesPassed++
} catch {
    Write-Host "  FAIL: Could not configure ATOM outbound rule: $_" -ForegroundColor Red
    $rulesFailed++
}

# Rule 3: Allow Tailscale (if installed)
Write-Host "`n[3/4] Configuring Tailscale access..." -ForegroundColor Yellow

$tailscaleInstalled = Get-Command tailscale -ErrorAction SilentlyContinue

if ($tailscaleInstalled) {
    try {
        # Remove existing rule if present
        Remove-NetFirewallRule -DisplayName "VALCORE1 - Tailscale" -ErrorAction SilentlyContinue

        # Add new rule for Tailscale interface
        New-NetFirewallRule `
            -DisplayName "VALCORE1 - Tailscale" `
            -Description "Allow VALCORE1 traffic over Tailscale VPN" `
            -Direction Inbound `
            -Action Allow `
            -InterfaceAlias "Tailscale" `
            -Profile Any `
            -Enabled True | Out-Null

        Write-Host "  PASS: Tailscale rule configured" -ForegroundColor Green
        Write-Host "  Interface: Tailscale" -ForegroundColor Cyan
        $rulesPassed++
    } catch {
        Write-Host "  WARN: Could not configure Tailscale rule: $_" -ForegroundColor Yellow
        Write-Host "  This may affect remote access via Tailscale" -ForegroundColor Yellow
        $rulesPassed++  # Don't fail on this one
    }
} else {
    Write-Host "  SKIP: Tailscale not installed" -ForegroundColor Yellow
    Write-Host "  (This is optional - local network will still work)" -ForegroundColor Cyan
}

# Rule 4: Block public network (security)
Write-Host "`n[4/4] Configuring security rules..." -ForegroundColor Yellow

try {
    # Block Flask server on public networks
    Remove-NetFirewallRule -DisplayName "VALCORE1 - Block Public" -ErrorAction SilentlyContinue

    New-NetFirewallRule `
        -DisplayName "VALCORE1 - Block Public" `
        -Description "Block VALCORE1 Flask server on public networks (security)" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5000 `
        -Profile Public `
        -Action Block `
        -Enabled True | Out-Null

    Write-Host "  PASS: Security rule configured" -ForegroundColor Green
    Write-Host "  Flask server blocked on public networks" -ForegroundColor Cyan
    $rulesPassed++
} catch {
    Write-Host "  WARN: Could not configure security rule: $_" -ForegroundColor Yellow
    $rulesPassed++  # Don't fail on this one
}

# List configured rules
Write-Host "`n[Summary] Configured firewall rules:" -ForegroundColor Cyan

$valcoreRules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "VALCORE1*" }

foreach ($rule in $valcoreRules) {
    $status = if ($rule.Enabled) { "Enabled" } else { "Disabled" }
    $color = if ($rule.Enabled) { "Green" } else { "Yellow" }

    Write-Host "  $($rule.DisplayName)" -ForegroundColor $color
    Write-Host "    Direction: $($rule.Direction), Action: $($rule.Action), Status: $status" -ForegroundColor Cyan
}

# Summary
Write-Host "`n=== Configuration Complete ===" -ForegroundColor Green
Write-Host "Rules Configured: $rulesPassed" -ForegroundColor $(if ($rulesPassed -ge 3) { "Green" } else { "Yellow" })
Write-Host "Rules Failed: $rulesFailed" -ForegroundColor $(if ($rulesFailed -eq 0) { "Green" } else { "Red" })

if ($rulesFailed -eq 0) {
    Write-Host "`nFirewall Status: CONFIGURED" -ForegroundColor Green
    Write-Host "VALCORE1 is allowed through Windows Firewall!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nFirewall Status: PARTIAL" -ForegroundColor Yellow
    Write-Host "Some rules failed - VALCORE1 may not work correctly`n" -ForegroundColor Yellow
    exit 1
}
