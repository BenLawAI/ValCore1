#Requires -RunAsAdministrator

# VALCORE1 Microphone Test
# Tests microphone detection and audio input

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Microphone Test ===" -ForegroundColor Cyan
Write-Host "Testing microphone detection and audio input`n"

$testsPassed = 0
$testsFailed = 0

# Test 1: Check audio libraries
Write-Host "[Test 1/4] Checking audio libraries..." -ForegroundColor Yellow

$audioTest = @"
import sys
try:
    import sounddevice as sd
    import numpy as np
    print('INSTALLED')
    sys.exit(0)
except ImportError as e:
    print(f'NOT_INSTALLED:{e}')
    sys.exit(1)
"@

try {
    $result = python -c $audioTest 2>$null

    if ($result -eq "INSTALLED") {
        Write-Host "  PASS: Audio libraries installed (sounddevice, numpy)" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "Audio libraries not installed"
    }
} catch {
    Write-Host "  FAIL: Audio libraries not installed" -ForegroundColor Red
    Write-Host "  Fix: Install with: pip install sounddevice numpy" -ForegroundColor Yellow
    $testsFailed++
}

# Test 2: Detect microphones
Write-Host "`n[Test 2/4] Detecting microphones..." -ForegroundColor Yellow

$micTest = @"
import sys
import sounddevice as sd

try:
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]

    if input_devices:
        print(f'FOUND:{len(input_devices)}')
        for i, dev in enumerate(input_devices):
            print(f'  [{i}] {dev["name"]} (channels: {dev["max_input_channels"]})')
        sys.exit(0)
    else:
        print('NO_DEVICES')
        sys.exit(1)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

try {
    $result = python -c $micTest 2>&1

    if ($result[0] -like "FOUND:*") {
        $deviceCount = $result[0] -replace "FOUND:", ""
        Write-Host "  PASS: Found $deviceCount microphone(s)" -ForegroundColor Green

        # Display device list
        for ($i = 1; $i -lt $result.Count; $i++) {
            Write-Host $result[$i] -ForegroundColor Cyan
        }

        $testsPassed++
    } else {
        throw "No microphones detected"
    }
} catch {
    Write-Host "  FAIL: No microphones detected" -ForegroundColor Red
    Write-Host "  Fix: Connect a microphone and ensure it's enabled in Windows Sound settings" -ForegroundColor Yellow
    $testsFailed++
}

# Test 3: Test default microphone
Write-Host "`n[Test 3/4] Testing default microphone..." -ForegroundColor Yellow

$defaultMicTest = @"
import sys
import sounddevice as sd

try:
    default_device = sd.query_devices(kind='input')

    if default_device and default_device['max_input_channels'] > 0:
        print(f'DEFAULT:{default_device["name"]}')
        sys.exit(0)
    else:
        print('NO_DEFAULT')
        sys.exit(1)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

try {
    $result = python -c $defaultMicTest 2>$null

    if ($result -like "DEFAULT:*") {
        $deviceName = $result -replace "DEFAULT:", ""
        Write-Host "  PASS: Default microphone detected: $deviceName" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "No default microphone"
    }
} catch {
    Write-Host "  FAIL: No default microphone configured" -ForegroundColor Red
    Write-Host "  Fix: Set a default input device in Windows Sound settings" -ForegroundColor Yellow
    $testsFailed++
}

# Test 4: Record audio sample
Write-Host "`n[Test 4/4] Recording audio sample..." -ForegroundColor Yellow
Write-Host "  This will record 2 seconds of audio to test microphone input" -ForegroundColor Cyan

$recordTest = @"
import sys
import sounddevice as sd
import numpy as np

try:
    print('Recording...', flush=True)

    # Record 2 seconds of audio
    sample_rate = 16000
    duration = 2
    audio = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype=np.float32)
    sd.wait()

    # Check if audio was captured
    max_amplitude = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio**2))

    print(f'RECORDED:max={max_amplitude:.4f},rms={rms:.4f}')

    if max_amplitude > 0.001:
        sys.exit(0)
    else:
        print('WARNING: Very low audio level detected')
        sys.exit(1)

except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
"@

try {
    Write-Host "  Recording for 2 seconds..." -ForegroundColor Cyan
    $result = python -c $recordTest 2>&1

    $recordLine = $result | Where-Object { $_ -like "RECORDED:*" }

    if ($recordLine) {
        Write-Host "  PASS: Audio recorded successfully" -ForegroundColor Green
        Write-Host "  $recordLine" -ForegroundColor Cyan
        $testsPassed++
    } else {
        throw "Recording failed"
    }
} catch {
    Write-Host "  FAIL: Could not record audio" -ForegroundColor Red
    Write-Host "  Fix: Check microphone permissions in Windows Privacy settings" -ForegroundColor Yellow
    Write-Host "       Settings > Privacy > Microphone > Allow apps to access microphone" -ForegroundColor Yellow
    $testsFailed++
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed/4" -ForegroundColor $(if ($testsPassed -eq 4) { "Green" } else { "Yellow" })
Write-Host "Tests Failed: $testsFailed/4" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`nMicrophone Status: READY" -ForegroundColor Green
    Write-Host "Your microphone is working correctly!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nMicrophone Status: NOT READY" -ForegroundColor Red
    Write-Host "Please fix the issues above before running VALCORE1`n" -ForegroundColor Yellow
    exit 1
}
