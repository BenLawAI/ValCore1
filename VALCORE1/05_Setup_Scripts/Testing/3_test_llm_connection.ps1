#Requires -RunAsAdministrator

# VALCORE1 LLM Connection Test
# Tests connection to ATOM server and LLM functionality

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 LLM Connection Test ===" -ForegroundColor Cyan
Write-Host "This script will test LLM connectivity and response generation`n"

# Load network config
$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Network config not found: $configPath" -ForegroundColor Red
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  ATOM IP: $($config.atom_local_ip)" -ForegroundColor White
Write-Host "  Ollama Port: $($config.ollama_port)" -ForegroundColor White
Write-Host "  Timeout: $($config.timeout_seconds)s`n" -ForegroundColor White

# Test 1: Ping ATOM server
Write-Host "[Test 1/4] Testing ATOM server connectivity..." -ForegroundColor Yellow

try {
    $pingResult = Test-Connection -ComputerName $config.atom_local_ip -Count 2 -Quiet

    if ($pingResult) {
        Write-Host "  PASS: ATOM server reachable" -ForegroundColor Green
    } else {
        throw "Cannot ping ATOM server"
    }
} catch {
    Write-Host "  FAIL: ATOM server not reachable" -ForegroundColor Red
    Write-Host "  Please ensure ATOM server is powered on and connected`n" -ForegroundColor Yellow
    exit 1
}

# Test 2: Test Ollama API
Write-Host "`n[Test 2/4] Testing Ollama API..." -ForegroundColor Yellow

$ollamaUrl = "http://$($config.atom_local_ip):$($config.ollama_port)/api/tags"

try {
    $response = Invoke-WebRequest -Uri $ollamaUrl -Method Get -TimeoutSec 10 -UseBasicParsing

    if ($response.StatusCode -eq 200) {
        $models = ($response.Content | ConvertFrom-Json).models

        Write-Host "  PASS: Ollama API responding" -ForegroundColor Green
        Write-Host "  Available models: $($models.Count)" -ForegroundColor Cyan

        if ($models.Count -gt 0) {
            Write-Host "  Models:" -ForegroundColor Cyan
            foreach ($model in $models) {
                Write-Host "    - $($model.name)" -ForegroundColor White
            }
        }
    } else {
        throw "Unexpected status code: $($response.StatusCode)"
    }
} catch {
    Write-Host "  FAIL: Ollama API not responding" -ForegroundColor Red
    Write-Host "  Please ensure Ollama is running on ATOM server`n" -ForegroundColor Yellow
    exit 1
}

# Test 3: Test LLM generation
Write-Host "`n[Test 3/4] Testing LLM generation..." -ForegroundColor Yellow

$generateUrl = "http://$($config.atom_local_ip):$($config.ollama_port)/api/generate"

$testPrompt = @{
    model = "qwen2.5:14b"
    prompt = "Respond with exactly: 'VALCORE1 test successful'"
    stream = $false
} | ConvertTo-Json

try {
    Write-Host "  Sending test prompt..." -ForegroundColor Cyan

    $response = Invoke-WebRequest -Uri $generateUrl -Method Post -Body $testPrompt -ContentType "application/json" -TimeoutSec 30 -UseBasicParsing

    if ($response.StatusCode -eq 200) {
        $result = $response.Content | ConvertFrom-Json

        Write-Host "  PASS: LLM generated response" -ForegroundColor Green
        Write-Host "  Response: $($result.response)" -ForegroundColor Cyan
    } else {
        throw "Unexpected status code: $($response.StatusCode)"
    }
} catch {
    Write-Host "  FAIL: LLM generation failed: $_" -ForegroundColor Red
    Write-Host "  This may indicate model not loaded or insufficient resources`n" -ForegroundColor Yellow
    exit 1
}

# Test 4: Test latency
Write-Host "`n[Test 4/4] Testing response latency..." -ForegroundColor Yellow

$latencyTests = @()

for ($i = 1; $i -le 3; $i++) {
    Write-Host "  Test $i/3..." -ForegroundColor Cyan

    $testPrompt = @{
        model = "qwen2.5:14b"
        prompt = "Say 'Test $i'"
        stream = $false
    } | ConvertTo-Json

    $startTime = Get-Date

    try {
        $response = Invoke-WebRequest -Uri $generateUrl -Method Post -Body $testPrompt -ContentType "application/json" -TimeoutSec 30 -UseBasicParsing

        $endTime = Get-Date
        $latency = ($endTime - $startTime).TotalMilliseconds

        $latencyTests += $latency

        Write-Host "    Latency: $([math]::Round($latency, 0)) ms" -ForegroundColor White
    } catch {
        Write-Host "    Failed: $_" -ForegroundColor Red
    }

    Start-Sleep -Milliseconds 500
}

if ($latencyTests.Count -gt 0) {
    $avgLatency = ($latencyTests | Measure-Object -Average).Average

    Write-Host "`n  Average latency: $([math]::Round($avgLatency, 0)) ms" -ForegroundColor Cyan

    if ($avgLatency -lt 5000) {
        Write-Host "  PASS: Good latency" -ForegroundColor Green
    } elseif ($avgLatency -lt 10000) {
        Write-Host "  PASS: Acceptable latency" -ForegroundColor Yellow
    } else {
        Write-Host "  WARN: High latency (may affect user experience)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "LLM Connection: OPERATIONAL" -ForegroundColor Green
Write-Host "ATOM server is responding correctly`n" -ForegroundColor Green

Write-Host "System is ready for voice assistant operations!`n" -ForegroundColor Green

exit 0
