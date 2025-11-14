#Requires -RunAsAdministrator

# VALCORE1 Master Test Suite
# Runs all diagnostic and system tests in sequence

$ErrorActionPreference = "Stop"

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  VALCORE1 MASTER TEST SUITE" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will run all VALCORE1 tests:" -ForegroundColor Yellow
Write-Host "  - Diagnostic tests (GPU, CUDA, microphone, network, Python)" -ForegroundColor White
Write-Host "  - System tests (full system, voice pipeline, LLM connection)" -ForegroundColor White
Write-Host "  - Estimated time: 5-10 minutes`n" -ForegroundColor White

$confirm = Read-Host "Run all tests? (Y/N)"

if ($confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

$scriptRoot = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts"

$diagnosticTests = @(
    "$scriptRoot\Diagnostic\1_test_gpu.ps1",
    "$scriptRoot\Diagnostic\2_test_cuda.ps1",
    "$scriptRoot\Diagnostic\3_test_microphone.ps1",
    "$scriptRoot\Diagnostic\4_test_network_atom.ps1",
    "$scriptRoot\Diagnostic\5_test_python_env.ps1"
)

$systemTests = @(
    "$scriptRoot\Testing\1_test_full_system.ps1",
    "$scriptRoot\Testing\2_test_voice_pipeline.ps1",
    "$scriptRoot\Testing\3_test_llm_connection.ps1"
)

$allTests = $diagnosticTests + $systemTests

$totalTests = $allTests.Count
$passedTests = 0
$failedTests = 0

$results = @()

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  PHASE 1: DIAGNOSTIC TESTS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

foreach ($test in $diagnosticTests) {
    $testName = Split-Path $test -Leaf

    Write-Host "`n--- Running: $testName ---" -ForegroundColor Yellow

    try {
        & $test

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Result: PASS" -ForegroundColor Green
            $passedTests++
            $results += @{ Test = $testName; Status = "PASS" }
        } else {
            Write-Host "  Result: FAIL" -ForegroundColor Red
            $failedTests++
            $results += @{ Test = $testName; Status = "FAIL" }
        }
    } catch {
        Write-Host "  Result: ERROR - $_" -ForegroundColor Red
        $failedTests++
        $results += @{ Test = $testName; Status = "ERROR" }
    }

    Start-Sleep -Seconds 2
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  PHASE 2: SYSTEM TESTS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

foreach ($test in $systemTests) {
    $testName = Split-Path $test -Leaf

    Write-Host "`n--- Running: $testName ---" -ForegroundColor Yellow

    try {
        & $test

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Result: PASS" -ForegroundColor Green
            $passedTests++
            $results += @{ Test = $testName; Status = "PASS" }
        } else {
            Write-Host "  Result: FAIL" -ForegroundColor Red
            $failedTests++
            $results += @{ Test = $testName; Status = "FAIL" }
        }
    } catch {
        Write-Host "  Result: ERROR - $_" -ForegroundColor Red
        $failedTests++
        $results += @{ Test = $testName; Status = "ERROR" }
    }

    Start-Sleep -Seconds 2
}

# Final Summary
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  FINAL TEST RESULTS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`nTest Results:" -ForegroundColor Yellow

foreach ($result in $results) {
    $color = if ($result.Status -eq "PASS") { "Green" } else { "Red" }
    $status = $result.Status.PadRight(5)

    Write-Host "  [$status] $($result.Test)" -ForegroundColor $color
}

Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  Total Tests: $totalTests" -ForegroundColor White
Write-Host "  Passed: $passedTests" -ForegroundColor Green
Write-Host "  Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Red" })

$passRate = [math]::Round(($passedTests / $totalTests) * 100, 1)
Write-Host "  Pass Rate: $passRate%" -ForegroundColor $(
    if ($passRate -eq 100) { "Green" }
    elseif ($passRate -ge 80) { "Yellow" }
    else { "Red" }
)

if ($failedTests -eq 0) {
    Write-Host "`n=========================================" -ForegroundColor Green
    Write-Host "  ALL TESTS PASSED" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "`nVALCORE1 is fully operational and ready to use!`n" -ForegroundColor Green
    exit 0
} elseif ($passRate -ge 80) {
    Write-Host "`n=========================================" -ForegroundColor Yellow
    Write-Host "  MOST TESTS PASSED" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Yellow
    Write-Host "`nVALCORE1 is mostly operational." -ForegroundColor Yellow
    Write-Host "Some optional features may not work.`n" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n=========================================" -ForegroundColor Red
    Write-Host "  TESTS FAILED" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "`nCritical issues detected." -ForegroundColor Red
    Write-Host "Please fix failed tests before using VALCORE1.`n" -ForegroundColor Red
    exit 1
}
