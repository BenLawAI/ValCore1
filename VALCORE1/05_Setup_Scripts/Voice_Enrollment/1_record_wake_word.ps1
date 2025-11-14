#Requires -RunAsAdministrator

# VALCORE1 Wake Word Recording
# Records custom wake word samples for Porcupine training

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Wake Word Recording ===" -ForegroundColor Cyan
Write-Host "This script will guide you through recording your custom wake word`n"

Write-Host "Important notes:" -ForegroundColor Yellow
Write-Host "  - You'll record the wake word 10 times" -ForegroundColor White
Write-Host "  - Say it naturally, as you would in daily use" -ForegroundColor White
Write-Host "  - Maintain consistent distance from microphone" -ForegroundColor White
Write-Host "  - Record in the environment where you'll use VALCORE1`n" -ForegroundColor White

# Check dependencies
$depsTest = @"
import sys
try:
    import sounddevice as sd
    import numpy as np
    import wave
    print('DEPS_OK')
except ImportError as e:
    print(f'MISSING:{e}')
    sys.exit(1)
"@

$result = python -c $depsTest 2>$null

if ($result -ne "DEPS_OK") {
    Write-Host "ERROR: Required libraries not installed" -ForegroundColor Red
    Write-Host "Install with: pip install sounddevice numpy`n" -ForegroundColor Yellow
    exit 1
}

# Create output directory
$outputDir = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\voice_profiles\wake_word_samples"

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Output directory: $outputDir`n" -ForegroundColor Cyan

# Get wake word
$wakeWord = Read-Host "Enter your wake word (e.g., 'Hey Val', 'Okay Val')"

if ([string]::IsNullOrWhiteSpace($wakeWord)) {
    Write-Host "ERROR: Wake word cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host "`nWake word: '$wakeWord'" -ForegroundColor Green
Write-Host "You will record this 10 times`n" -ForegroundColor Cyan

$confirm = Read-Host "Ready to start recording? (Y/N)"

if ($confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Recording script
$recordScript = @"
import sys
import sounddevice as sd
import numpy as np
import wave
from pathlib import Path

def record_sample(output_path, duration=2.0, sample_rate=16000):
    '''Record audio sample'''
    try:
        # Record
        audio = sd.rec(int(duration * sample_rate),
                      samplerate=sample_rate,
                      channels=1,
                      dtype=np.float32)
        sd.wait()

        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        # Save as WAV
        with wave.open(output_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

        # Check level
        max_amplitude = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio**2))

        return True, max_amplitude, rms

    except Exception as e:
        return False, 0, 0

# Main recording loop
output_dir = Path('$($outputDir.Replace('\', '/'))')
wake_word_safe = '$($wakeWord.Replace(' ', '_').Replace("'", ''))'

print('Starting recording session...')

for i in range(10):
    input(f'\nPress ENTER when ready to record sample {i+1}/10...')

    print(f'Recording {i+1}/10 - Say: "{wakeWord}"', flush=True)
    print('3...', flush=True)
    import time
    time.sleep(0.7)
    print('2...', flush=True)
    time.sleep(0.7)
    print('1...', flush=True)
    time.sleep(0.7)
    print('RECORDING NOW!', flush=True)

    output_path = output_dir / f'{wake_word_safe}_sample_{i+1:02d}.wav'
    success, max_amp, rms = record_sample(str(output_path))

    if success:
        print(f'  Saved: {output_path.name}')
        print(f'  Level: max={max_amp:.4f}, rms={rms:.4f}')

        if max_amp < 0.01:
            print('  WARNING: Audio level very low - speak louder!')
        elif max_amp > 0.9:
            print('  WARNING: Audio level very high - speak softer or move back!')
    else:
        print(f'  ERROR: Failed to record sample {i+1}')

print('\nRecording session complete!')
print(f'Samples saved to: {output_dir}')
"@

# Run recording
try {
    python -c $recordScript

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== Recording Complete ===" -ForegroundColor Green
    } else {
        throw "Recording script failed"
    }
} catch {
    Write-Host "`nERROR: Recording failed: $_" -ForegroundColor Red
    exit 1
}

# Count recorded files
$recordings = Get-ChildItem -Path $outputDir -Filter "*.wav"

Write-Host "`nRecorded samples: $($recordings.Count)/10" -ForegroundColor Cyan

if ($recordings.Count -eq 10) {
    Write-Host "All samples recorded successfully!" -ForegroundColor Green
} else {
    Write-Host "Some samples may be missing" -ForegroundColor Yellow
}

# Save wake word configuration
$wakeWordConfig = @{
    wake_word = $wakeWord
    samples_directory = $outputDir
    sample_count = $recordings.Count
    recorded_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    porcupine_model_path = ""  # Will be filled after training
}

$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\wake_word_config.json"

try {
    $wakeWordConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "`nConfiguration saved: $configPath" -ForegroundColor Green
} catch {
    Write-Host "`nWARN: Could not save configuration: $_" -ForegroundColor Yellow
}

# Next steps
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review your recordings in: $outputDir" -ForegroundColor White
Write-Host "  2. Upload samples to Picovoice Console: https://console.picovoice.ai/" -ForegroundColor White
Write-Host "  3. Train custom wake word model" -ForegroundColor White
Write-Host "  4. Download .ppn model file" -ForegroundColor White
Write-Host "  5. Place model in: VALCORE1\01_Client_Brain\models\wake_word.ppn`n" -ForegroundColor White

exit 0
