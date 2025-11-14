#Requires -RunAsAdministrator

# VALCORE1 Audio Device Configuration
# Configures and tests audio input/output devices for VALCORE1

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Audio Device Configuration ===" -ForegroundColor Cyan
Write-Host "This script will help you configure audio devices for VALCORE1`n"

# Check audio libraries
$audioTest = @"
import sys
try:
    import sounddevice as sd
    import numpy as np
    print('AUDIO_OK')
except ImportError:
    print('AUDIO_MISSING')
    sys.exit(1)
"@

$result = python -c $audioTest 2>$null

if ($result -ne "AUDIO_OK") {
    Write-Host "ERROR: Audio libraries not installed" -ForegroundColor Red
    Write-Host "Install with: pip install sounddevice numpy`n" -ForegroundColor Yellow
    exit 1
}

# List all audio devices
Write-Host "[1/4] Detecting audio devices..." -ForegroundColor Yellow

$listDevices = @"
import sounddevice as sd

devices = sd.query_devices()

print('\n=== Input Devices (Microphones) ===')
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        default_marker = ' [DEFAULT]' if i == sd.default.device[0] else ''
        print(f'{i}: {dev["name"]}{default_marker}')
        print(f'   Channels: {dev["max_input_channels"]}, Sample Rate: {dev["default_samplerate"]:.0f} Hz')

print('\n=== Output Devices (Speakers) ===')
for i, dev in enumerate(devices):
    if dev['max_output_channels'] > 0:
        default_marker = ' [DEFAULT]' if i == sd.default.device[1] else ''
        print(f'{i}: {dev["name"]}{default_marker}')
        print(f'   Channels: {dev["max_output_channels"]}, Sample Rate: {dev["default_samplerate"]:.0f} Hz')
"@

python -c $listDevices | ForEach-Object {
    if ($_ -like "=== *") {
        Write-Host $_ -ForegroundColor Cyan
    } elseif ($_ -like "*[DEFAULT]*") {
        Write-Host $_ -ForegroundColor Green
    } else {
        Write-Host $_ -ForegroundColor White
    }
}

# Configure input device
Write-Host "`n[2/4] Configuring input device..." -ForegroundColor Yellow

$useDefault = Read-Host "Use default microphone? (Y/N)"

$inputDeviceId = $null

if ($useDefault -eq 'Y') {
    Write-Host "  Using default input device" -ForegroundColor Green
    $inputDeviceId = -1  # -1 means use system default
} else {
    $deviceId = Read-Host "Enter input device ID"

    try {
        $inputDeviceId = [int]$deviceId
        Write-Host "  Input device set to: $inputDeviceId" -ForegroundColor Green
    } catch {
        Write-Host "  Invalid device ID, using default" -ForegroundColor Yellow
        $inputDeviceId = -1
    }
}

# Test recording
Write-Host "`n[3/4] Testing microphone..." -ForegroundColor Yellow

$recordTest = @"
import sys
import sounddevice as sd
import numpy as np

try:
    device_id = $inputDeviceId if $inputDeviceId >= 0 else None

    print('Recording 2 seconds...')

    # Record
    sample_rate = 16000
    duration = 2
    audio = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   device=device_id,
                   dtype=np.float32)
    sd.wait()

    # Analyze
    max_amplitude = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio**2))

    print(f'Max amplitude: {max_amplitude:.4f}')
    print(f'RMS level: {rms:.4f}')

    if max_amplitude > 0.001:
        print('RECORDING_OK')
        sys.exit(0)
    else:
        print('RECORDING_SILENT')
        sys.exit(1)

except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

Write-Host "  Speak into your microphone for 2 seconds..." -ForegroundColor Cyan
Write-Host "  (Say something like: 'Testing, one, two, three')" -ForegroundColor Cyan

$testResult = python -c $recordTest 2>&1

if ($testResult -contains "RECORDING_OK") {
    Write-Host "  PASS: Microphone working correctly!" -ForegroundColor Green

    $levels = $testResult | Where-Object { $_ -match "amplitude|RMS" }
    foreach ($level in $levels) {
        Write-Host "  $level" -ForegroundColor Cyan
    }
} else {
    Write-Host "  WARN: Recording level very low or silent" -ForegroundColor Yellow
    Write-Host "  Check microphone volume in Windows Sound settings" -ForegroundColor Yellow
}

# Save configuration
Write-Host "`n[4/4] Saving audio configuration..." -ForegroundColor Yellow

$audioConfig = @{
    input_device_id = $inputDeviceId
    sample_rate = 16000
    channels = 1
    chunk_duration_ms = 100
    auto_adjust_volume = $true
    noise_suppression = $true
    echo_cancellation = $true
}

$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\audio_config.json"

try {
    $audioConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "  Audio config saved: $configPath" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: Could not save audio config: $_" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n=== Configuration Complete ===" -ForegroundColor Green
Write-Host "`nAudio settings:" -ForegroundColor Cyan
Write-Host "  Input device: $(if ($inputDeviceId -eq -1) { 'System default' } else { "Device $inputDeviceId" })" -ForegroundColor White
Write-Host "  Sample rate: 16000 Hz" -ForegroundColor White
Write-Host "  Channels: 1 (mono)" -ForegroundColor White
Write-Host "  Auto-adjust volume: Enabled" -ForegroundColor White
Write-Host "  Noise suppression: Enabled" -ForegroundColor White
Write-Host "  Echo cancellation: Enabled`n" -ForegroundColor White

Write-Host "Audio configuration complete!" -ForegroundColor Green
Write-Host "VALCORE1 will use these settings for voice input.`n" -ForegroundColor Green

exit 0
