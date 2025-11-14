#Requires -RunAsAdministrator

# VALCORE1 Voice Profile Recording
# Records Ben's voice for speaker verification using training phrases

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Voice Profile Recording ===" -ForegroundColor Cyan
Write-Host "This script will record your voice to create a speaker verification profile`n"

Write-Host "Important notes:" -ForegroundColor Yellow
Write-Host "  - You'll read training phrases from a file" -ForegroundColor White
Write-Host "  - Speak naturally and clearly" -ForegroundColor White
Write-Host "  - Use consistent microphone distance" -ForegroundColor White
Write-Host "  - Record in a quiet environment`n" -ForegroundColor White

# Check dependencies
$depsTest = @"
import sys
try:
    import sounddevice as sd
    import numpy as np
    import wave
    print('DEPS_OK')
except ImportError:
    print('DEPS_MISSING')
    sys.exit(1)
"@

$result = python -c $depsTest 2>$null

if ($result -ne "DEPS_OK") {
    Write-Host "ERROR: Required libraries not installed" -ForegroundColor Red
    Write-Host "Install with: pip install sounddevice numpy`n" -ForegroundColor Yellow
    exit 1
}

# Check training phrases file
$phrasesPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\03_Shared\training_phrases.txt"

if (-not (Test-Path $phrasesPath)) {
    Write-Host "ERROR: Training phrases file not found: $phrasesPath" -ForegroundColor Red
    exit 1
}

# Load training phrases
$phrases = Get-Content $phrasesPath | Where-Object { $_ -notmatch "^#" -and $_ -notmatch "^\s*$" }

Write-Host "Loaded $($phrases.Count) training phrases" -ForegroundColor Green

# Create output directory
$outputDir = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\voice_profiles\ben_voice_samples"

if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Output directory: $outputDir`n" -ForegroundColor Cyan

# Get speaker name
$speakerName = Read-Host "Enter speaker name (default: Ben)"

if ([string]::IsNullOrWhiteSpace($speakerName)) {
    $speakerName = "Ben"
}

Write-Host "`nSpeaker: $speakerName" -ForegroundColor Green
Write-Host "You will read $($phrases.Count) phrases`n" -ForegroundColor Cyan

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

def record_sample(output_path, duration=5.0, sample_rate=16000):
    '''Record audio sample'''
    try:
        audio = sd.rec(int(duration * sample_rate),
                      samplerate=sample_rate,
                      channels=1,
                      dtype=np.float32)
        sd.wait()

        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)

        # Save
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
        print(f'ERROR: {e}')
        return False, 0, 0

# Load phrases
phrases_path = Path('$($phrasesPath.Replace('\', '/'))')
with open(phrases_path, 'r') as f:
    phrases = [line.strip() for line in f if line.strip() and not line.startswith('#')]

output_dir = Path('$($outputDir.Replace('\', '/'))')
speaker_name = '$speakerName'

print(f'\nRecording {len(phrases)} phrases for speaker: {speaker_name}\n')

successful_recordings = 0

for i, phrase in enumerate(phrases):
    print(f'\n[{i+1}/{len(phrases)}] Press ENTER when ready...')
    input()

    print(f'READ THIS: {phrase}', flush=True)
    print('Recording in 3...', flush=True)

    import time
    time.sleep(0.7)
    print('2...', flush=True)
    time.sleep(0.7)
    print('1...', flush=True)
    time.sleep(0.7)
    print('RECORDING NOW (you have 5 seconds)!', flush=True)

    output_path = output_dir / f'{speaker_name.lower()}_phrase_{i+1:03d}.wav'
    success, max_amp, rms = record_sample(str(output_path))

    if success:
        print(f'  Saved: {output_path.name}')
        print(f'  Level: max={max_amp:.4f}, rms={rms:.4f}')

        if max_amp < 0.01:
            print('  WARNING: Very low - speak louder!')
        elif max_amp > 0.9:
            print('  WARNING: Clipping - speak softer!')
        else:
            successful_recordings += 1
    else:
        print(f'  ERROR: Failed to record phrase {i+1}')

    # Allow retry
    if not success or max_amp < 0.01:
        retry = input('  Retry this phrase? (Y/N): ')
        if retry.upper() == 'Y':
            print('  Retrying...')
            # Re-record
            success, max_amp, rms = record_sample(str(output_path))
            if success and max_amp >= 0.01:
                successful_recordings += 1

print(f'\n=== Recording Complete ===')
print(f'Successfully recorded: {successful_recordings}/{len(phrases)} phrases')
"@

# Run recording
try {
    python -c $recordScript

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== Recording Session Complete ===" -ForegroundColor Green
    } else {
        throw "Recording script failed"
    }
} catch {
    Write-Host "`nERROR: Recording failed: $_" -ForegroundColor Red
    exit 1
}

# Count recorded files
$recordings = Get-ChildItem -Path $outputDir -Filter "*.wav"

Write-Host "`nTotal recordings: $($recordings.Count)" -ForegroundColor Cyan

if ($recordings.Count -ge 20) {
    Write-Host "Sufficient samples for voice profile creation!" -ForegroundColor Green
} else {
    Write-Host "WARNING: Less than 20 samples - voice verification may be less accurate" -ForegroundColor Yellow
}

# Save voice profile configuration
$voiceProfileConfig = @{
    speaker_name = $speakerName
    samples_directory = $outputDir
    sample_count = $recordings.Count
    recorded_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    embeddings_file = "$outputDir\embeddings.npy"  # Will be created in next step
}

$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\voice_profile_config.json"

try {
    $voiceProfileConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "`nConfiguration saved: $configPath" -ForegroundColor Green
} catch {
    Write-Host "`nWARN: Could not save configuration: $_" -ForegroundColor Yellow
}

# Next steps
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Run: 3_create_voice_embeddings.ps1" -ForegroundColor White
Write-Host "  2. This will create voice embeddings from your recordings" -ForegroundColor White
Write-Host "  3. Then test with: 4_test_voice_verification.ps1`n" -ForegroundColor White

exit 0
