#Requires -RunAsAdministrator

# VALCORE1 Full System Test
# Comprehensive test of all VALCORE1 components

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Full System Test ===" -ForegroundColor Cyan
Write-Host "This script will test all VALCORE1 components end-to-end`n"

$totalTests = 0
$passedTests = 0
$failedTests = 0
$warnings = 0

function Test-Component {
    param(
        [string]$Name,
        [scriptblock]$TestScript
    )

    $script:totalTests++

    Write-Host "`n[$script:totalTests] Testing: $Name" -ForegroundColor Yellow

    try {
        $result = & $TestScript

        if ($result) {
            Write-Host "  PASS" -ForegroundColor Green
            $script:passedTests++
            return $true
        } else {
            Write-Host "  FAIL" -ForegroundColor Red
            $script:failedTests++
            return $false
        }
    } catch {
        Write-Host "  FAIL: $_" -ForegroundColor Red
        $script:failedTests++
        return $false
    }
}

# Test 1: Python Environment
Test-Component "Python Environment" {
    $pythonTest = python --version 2>&1
    return $pythonTest -match "Python 3\.1[0-9]"
}

# Test 2: GPU Detection
Test-Component "GPU Detection" {
    $gpuTest = @"
import torch
print(torch.cuda.is_available() and torch.cuda.device_count() >= 2)
"@
    $result = python -c $gpuTest 2>$null
    return $result -eq "True"
}

# Test 3: Voice Libraries
Test-Component "Voice Libraries" {
    $voiceTest = @"
try:
    import sounddevice
    import faster_whisper
    print('True')
except:
    print('False')
"@
    $result = python -c $voiceTest 2>$null
    return $result -eq "True"
}

# Test 4: Microphone Detection
Test-Component "Microphone Detection" {
    $micTest = @"
import sounddevice as sd
devices = [d for d in sd.query_devices() if d['max_input_channels'] > 0]
print(len(devices) > 0)
"@
    $result = python -c $micTest 2>$null
    return $result -eq "True"
}

# Test 5: Network Config
Test-Component "Network Configuration" {
    $configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json"
    return Test-Path $configPath
}

# Test 6: ATOM Server Connectivity
Test-Component "ATOM Server Connectivity" {
    $configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json"

    if (Test-Path $configPath) {
        $config = Get-Content $configPath | ConvertFrom-Json
        $atomIP = $config.atom_local_ip

        try {
            $ping = Test-Connection -ComputerName $atomIP -Count 1 -Quiet
            return $ping
        } catch {
            return $false
        }
    }

    return $false
}

# Test 7: Ollama API
Test-Component "Ollama API" {
    $configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json"

    if (Test-Path $configPath) {
        $config = Get-Content $configPath | ConvertFrom-Json
        $ollamaUrl = "http://$($config.atom_local_ip):$($config.ollama_port)/api/tags"

        try {
            $response = Invoke-WebRequest -Uri $ollamaUrl -Method Get -TimeoutSec 5 -UseBasicParsing
            return $response.StatusCode -eq 200
        } catch {
            return $false
        }
    }

    return $false
}

# Test 8: Client Brain Modules
Test-Component "Client Brain Modules" {
    $modulesExist = @(
        "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\core\voice_system_unified.py",
        "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\core\server_bridge.py",
        "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\core\automation.py"
    )

    foreach ($module in $modulesExist) {
        if (-not (Test-Path $module)) {
            return $false
        }
    }

    return $true
}

# Test 9: Server Brain Modules
Test-Component "Server Brain Modules" {
    $modulesExist = @(
        "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\02_Server_Brain\core\large_llm_interface.py",
        "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\02_Server_Brain\core\librarian.py",
        "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\02_Server_Brain\core\client_bridge.py"
    )

    foreach ($module in $modulesExist) {
        if (-not (Test-Path $module)) {
            return $false
        }
    }

    return $true
}

# Test 10: Voice System Import
Test-Component "Voice System Import" {
    $importTest = @"
import sys
sys.path.insert(0, 'A:/000_START_HERE/VALCORE1_ROOT/Systems/VALCORE1')
try:
    from VALCORE1.client_brain.core.voice_system_unified import VoiceSystemUnified
    print('True')
except Exception as e:
    print('False')
"@
    $result = python -c $importTest 2>$null
    return $result -eq "True"
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })

$passRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "`nPass Rate: $passRate%" -ForegroundColor $(
    if ($passRate -eq 100) { "Green" }
    elseif ($passRate -ge 80) { "Yellow" }
    else { "Red" }
)

if ($failedTests -eq 0) {
    Write-Host "`nSystem Status: READY" -ForegroundColor Green
    Write-Host "All systems operational! VALCORE1 is ready to run.`n" -ForegroundColor Green
    exit 0
} elseif ($passRate -ge 80) {
    Write-Host "`nSystem Status: MOSTLY READY" -ForegroundColor Yellow
    Write-Host "Most systems operational. Some optional features may not work.`n" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`nSystem Status: NOT READY" -ForegroundColor Red
    Write-Host "Critical systems failed. Please fix issues before running VALCORE1.`n" -ForegroundColor Red
    exit 1
}
