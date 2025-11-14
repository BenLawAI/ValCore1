#Requires -RunAsAdministrator

# VALCORE1 Startup Configuration
# Configures VALCORE1 to start automatically with Windows

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Startup Configuration ===" -ForegroundColor Cyan
Write-Host "This script will configure VALCORE1 to start automatically with Windows`n"

$confirm = Read-Host "Do you want VALCORE1 to start automatically? (Y/N)"

if ($confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Paths
$valcoreRoot = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1"
$startupBat = "$valcoreRoot\START_VALCORE1.bat"
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = "$startupFolder\VALCORE1.lnk"

# Verify startup script exists
if (-not (Test-Path $startupBat)) {
    Write-Host "ERROR: Startup script not found: $startupBat" -ForegroundColor Red
    Write-Host "Please ensure VALCORE1 is properly installed`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/3] Creating startup shortcut..." -ForegroundColor Yellow

try {
    # Create WScript Shell object
    $WshShell = New-Object -ComObject WScript.Shell

    # Create shortcut
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $startupBat
    $Shortcut.WorkingDirectory = $valcoreRoot
    $Shortcut.Description = "VALCORE1 Voice Assistant"
    $Shortcut.WindowStyle = 7  # Minimized
    $Shortcut.Save()

    Write-Host "  Shortcut created: $shortcutPath" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: Could not create shortcut: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/3] Configuring startup options..." -ForegroundColor Yellow

# Create startup config
$startupConfig = @{
    enabled = $true
    minimized = $true
    auto_start_microphone = $true
    default_room = "general"
    startup_delay_seconds = 5
}

$configPath = "$valcoreRoot\01_Client_Brain\config\startup_config.json"

try {
    $startupConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "  Startup config saved: $configPath" -ForegroundColor Green
} catch {
    Write-Host "  WARN: Could not save startup config: $_" -ForegroundColor Yellow
}

Write-Host "`n[3/3] Testing startup configuration..." -ForegroundColor Yellow

if (Test-Path $shortcutPath) {
    Write-Host "  Startup shortcut verified" -ForegroundColor Green
} else {
    Write-Host "  WARN: Startup shortcut not found" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Configuration Complete ===" -ForegroundColor Green
Write-Host "`nStartup configuration:" -ForegroundColor Cyan
Write-Host "  Status: Enabled" -ForegroundColor White
Write-Host "  Shortcut: $shortcutPath" -ForegroundColor White
Write-Host "  Window: Minimized" -ForegroundColor White
Write-Host "  Auto-start microphone: Yes" -ForegroundColor White
Write-Host "  Default room: general" -ForegroundColor White
Write-Host "  Startup delay: 5 seconds`n" -ForegroundColor White

Write-Host "VALCORE1 will now start automatically when Windows starts!" -ForegroundColor Green
Write-Host "`nTo disable automatic startup:" -ForegroundColor Yellow
Write-Host "  Delete: $shortcutPath`n" -ForegroundColor Yellow

exit 0
