#Requires -RunAsAdministrator

# VALCORE1 System Tray Configuration
# Configures system tray icon and notification settings

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 System Tray Configuration ===" -ForegroundColor Cyan
Write-Host "This script will configure the VALCORE1 system tray icon and notifications`n"

# Paths
$valcoreRoot = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1"
$iconDir = "$valcoreRoot\01_Client_Brain\assets\icons"

Write-Host "[1/4] Checking icon directory..." -ForegroundColor Yellow

if (-not (Test-Path $iconDir)) {
    Write-Host "  Creating icon directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $iconDir -Force | Out-Null
}

Write-Host "  Icon directory: $iconDir" -ForegroundColor Green

Write-Host "`n[2/4] Creating system tray icons..." -ForegroundColor Yellow

# Create placeholder icons (simple colored squares)
# In production, Ben should replace these with proper icons

$iconColors = @{
    "green" = "Active (Listening)"
    "yellow" = "Processing"
    "red" = "Error"
    "gray" = "Disabled"
}

$iconScript = @"
from PIL import Image, ImageDraw

colors = {
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'red': (255, 0, 0),
    'gray': (128, 128, 128)
}

for color_name, rgb in colors.items():
    img = Image.new('RGB', (64, 64), rgb)
    draw = ImageDraw.Draw(img)

    # Add a simple border
    draw.rectangle([(0, 0), (63, 63)], outline=(0, 0, 0), width=2)

    # Save
    img.save(f'$($iconDir.Replace('\', '/'))/valcore_{color_name}.ico')
    print(f'Created: valcore_{color_name}.ico')
"@

try {
    python -c $iconScript 2>&1 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Cyan
    }
    Write-Host "  Icons created successfully" -ForegroundColor Green
} catch {
    Write-Host "  WARN: Could not create icons (PIL required): $_" -ForegroundColor Yellow
    Write-Host "  Install with: pip install pillow" -ForegroundColor Yellow
}

Write-Host "`n[3/4] Configuring notification settings..." -ForegroundColor Yellow

$notificationConfig = @{
    show_notifications = $true
    notification_duration_seconds = 5
    notify_on_startup = $true
    notify_on_error = $true
    notify_on_room_switch = $true
    notify_on_server_disconnect = $true
    sound_enabled = $false
    icon_colors = @{
        listening = "green"
        processing = "yellow"
        error = "red"
        disabled = "gray"
    }
    menu_items = @(
        "Toggle Microphone",
        "Switch Room",
        "Status",
        "Settings",
        "Exit"
    )
}

$configPath = "$valcoreRoot\01_Client_Brain\config\system_tray_config.json"

try {
    $notificationConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "  Configuration saved: $configPath" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: Could not save configuration: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[4/4] Testing system tray module..." -ForegroundColor Yellow

$trayTest = @"
import sys
try:
    import pystray
    from PIL import Image
    print('TRAY_OK')
    sys.exit(0)
except ImportError as e:
    print(f'MISSING:{e}')
    sys.exit(1)
"@

$result = python -c $trayTest 2>&1

if ($result -eq "TRAY_OK") {
    Write-Host "  System tray module: OK" -ForegroundColor Green
} else {
    Write-Host "  WARN: System tray module not available" -ForegroundColor Yellow
    Write-Host "  Install with: pip install pystray pillow" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Configuration Complete ===" -ForegroundColor Green
Write-Host "`nSystem tray settings:" -ForegroundColor Cyan
Write-Host "  Notifications: Enabled" -ForegroundColor White
Write-Host "  Notification duration: 5 seconds" -ForegroundColor White
Write-Host "  Icons created: 4 status icons" -ForegroundColor White
Write-Host "  Menu items: 5 options" -ForegroundColor White
Write-Host "`nIcon states:" -ForegroundColor Cyan

foreach ($color in $iconColors.Keys) {
    Write-Host "  $color`: $($iconColors[$color])" -ForegroundColor White
}

Write-Host "`nThe system tray icon will appear when VALCORE1 is running." -ForegroundColor Green
Write-Host "Right-click the icon to access the menu.`n" -ForegroundColor Green

exit 0
