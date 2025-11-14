#Requires -RunAsAdministrator

# VALCORE1 Network Test (ATOM Server)
# Tests network connectivity to ATOM server

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Network Test (ATOM Server) ===" -ForegroundColor Cyan
Write-Host "Testing connectivity to ATOM server`n"

# Load network config
$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Network config not found: $configPath" -ForegroundColor Red
    Write-Host "Please ensure VALCORE1 is properly installed`n" -ForegroundColor Yellow
    exit 1
}

try {
    $config = Get-Content $configPath | ConvertFrom-Json
} catch {
    Write-Host "ERROR: Could not parse network config: $_" -ForegroundColor Red
    exit 1
}

$testsPassed = 0
$testsFailed = 0

# Test 1: Check local network connectivity
Write-Host "[Test 1/5] Testing local network connectivity..." -ForegroundColor Yellow

$localIP = $config.atom_local_ip
$localPort = $config.ollama_port

Write-Host "  Target: $localIP`:$localPort" -ForegroundColor Cyan

try {
    $pingResult = Test-Connection -ComputerName $localIP -Count 2 -Quiet

    if ($pingResult) {
        Write-Host "  PASS: ATOM server reachable on local network" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "Cannot ping ATOM server"
    }
} catch {
    Write-Host "  FAIL: Cannot reach ATOM server on local network" -ForegroundColor Red
    Write-Host "  Fix: Verify ATOM server IP address ($localIP) and network connection" -ForegroundColor Yellow
    $testsFailed++
}

# Test 2: Test Ollama port
Write-Host "`n[Test 2/5] Testing Ollama port connectivity..." -ForegroundColor Yellow

try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $connect = $tcpClient.BeginConnect($localIP, $localPort, $null, $null)
    $wait = $connect.AsyncWaitHandle.WaitOne(5000, $false)

    if ($wait -and $tcpClient.Connected) {
        Write-Host "  PASS: Ollama port ($localPort) is accessible" -ForegroundColor Green
        $tcpClient.Close()
        $testsPassed++
    } else {
        $tcpClient.Close()
        throw "Port not accessible"
    }
} catch {
    Write-Host "  FAIL: Cannot connect to Ollama port ($localPort)" -ForegroundColor Red
    Write-Host "  Fix: Ensure Ollama is running on ATOM server" -ForegroundColor Yellow
    Write-Host "       On ATOM, run: systemctl status ollama" -ForegroundColor Yellow
    $testsFailed++
}

# Test 3: Test Ollama API
Write-Host "`n[Test 3/5] Testing Ollama API..." -ForegroundColor Yellow

try {
    $ollamaUrl = "http://$localIP`:$localPort/api/tags"
    Write-Host "  Querying: $ollamaUrl" -ForegroundColor Cyan

    $response = Invoke-WebRequest -Uri $ollamaUrl -Method Get -TimeoutSec 10 -UseBasicParsing

    if ($response.StatusCode -eq 200) {
        $models = ($response.Content | ConvertFrom-Json).models
        Write-Host "  PASS: Ollama API responding ($($models.Count) models available)" -ForegroundColor Green

        # List models
        if ($models.Count -gt 0) {
            Write-Host "  Available models:" -ForegroundColor Cyan
            foreach ($model in $models) {
                Write-Host "    - $($model.name)" -ForegroundColor Cyan
            }
        }

        $testsPassed++
    } else {
        throw "Unexpected status code: $($response.StatusCode)"
    }
} catch {
    Write-Host "  FAIL: Ollama API not responding" -ForegroundColor Red
    Write-Host "  Fix: Verify Ollama is installed and running on ATOM" -ForegroundColor Yellow
    Write-Host "       On ATOM, run: curl http://localhost:11434/api/tags" -ForegroundColor Yellow
    $testsFailed++
}

# Test 4: Test Tailscale connectivity (if configured)
Write-Host "`n[Test 4/5] Testing Tailscale connectivity..." -ForegroundColor Yellow

if ($config.atom_tailscale_ip -and $config.prefer_tailscale) {
    $tailscaleIP = $config.atom_tailscale_ip
    Write-Host "  Target: $tailscaleIP`:$localPort" -ForegroundColor Cyan

    try {
        $pingResult = Test-Connection -ComputerName $tailscaleIP -Count 2 -Quiet

        if ($pingResult) {
            Write-Host "  PASS: ATOM reachable via Tailscale" -ForegroundColor Green
            $testsPassed++
        } else {
            throw "Cannot ping Tailscale IP"
        }
    } catch {
        Write-Host "  FAIL: Cannot reach ATOM via Tailscale" -ForegroundColor Red
        Write-Host "  Fix: Verify both devices are connected to Tailscale network" -ForegroundColor Yellow
        Write-Host "       Run: tailscale status" -ForegroundColor Yellow
        $testsFailed++
    }
} else {
    Write-Host "  SKIP: Tailscale not configured" -ForegroundColor Yellow
    Write-Host "  (This is optional - local network is working)" -ForegroundColor Cyan
}

# Test 5: Test network latency
Write-Host "`n[Test 5/5] Testing network latency..." -ForegroundColor Yellow

try {
    $pingTests = Test-Connection -ComputerName $localIP -Count 5
    $avgLatency = ($pingTests | Measure-Object -Property ResponseTime -Average).Average

    Write-Host "  Average latency: $([math]::Round($avgLatency, 2)) ms" -ForegroundColor Cyan

    if ($avgLatency -lt 50) {
        Write-Host "  PASS: Excellent network latency" -ForegroundColor Green
        $testsPassed++
    } elseif ($avgLatency -lt 100) {
        Write-Host "  PASS: Good network latency" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  WARN: High latency detected (may affect performance)" -ForegroundColor Yellow
        Write-Host "  Consider using Tailscale or checking network configuration" -ForegroundColor Yellow
        $testsPassed++
    }
} catch {
    Write-Host "  FAIL: Could not measure latency" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed/5" -ForegroundColor $(if ($testsPassed -ge 4) { "Green" } else { "Yellow" })
Write-Host "Tests Failed: $testsFailed/5" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`nNetwork Status: READY" -ForegroundColor Green
    Write-Host "ATOM server connectivity is working correctly!`n" -ForegroundColor Green
    exit 0
} elseif ($testsPassed -ge 3) {
    Write-Host "`nNetwork Status: PARTIAL" -ForegroundColor Yellow
    Write-Host "Some features may not work - check warnings above`n" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`nNetwork Status: NOT READY" -ForegroundColor Red
    Write-Host "Please fix the issues above before running VALCORE1`n" -ForegroundColor Yellow
    exit 1
}
