#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Setup Piper-TTS voice models for VALCORE1

.DESCRIPTION
    Downloads and configures Piper-TTS voice models for text-to-speech functionality.
    This script will:
    - Install piper-tts Python package
    - Download the default voice model (en_US-lessac-medium)
    - Configure the voice system
    - Test TTS functionality

.NOTES
    Author: VALCORE1 Team
    Requires: Python 3.10+, pip
#>

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "VALCORE1 - Piper TTS Setup" -ForegroundColor Cyan
Write-Host "==================================`n" -ForegroundColor Cyan

# Configuration
$VOICE_MODEL = "en_US-lessac-medium"
$MODELS_DIR = "models/piper"
$VOICE_CONFIG = "01_Client_Brain/config/voice_config.json"

# Step 1: Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

# Step 2: Install piper-tts
Write-Host "`n[2/5] Installing piper-tts package..." -ForegroundColor Yellow

try {
    pip install piper-tts --quiet
    Write-Host "  ✓ piper-tts installed successfully" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to install piper-tts" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Create models directory
Write-Host "`n[3/5] Creating models directory..." -ForegroundColor Yellow

try {
    if (!(Test-Path -Path $MODELS_DIR)) {
        New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null
    }
    Write-Host "  ✓ Models directory ready: $MODELS_DIR" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to create models directory" -ForegroundColor Red
    exit 1
}

# Step 4: Download voice model
Write-Host "`n[4/5] Downloading voice model ($VOICE_MODEL)..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

try {
    # Piper will auto-download on first use, but we can pre-download
    python -c @"
from piper.download import ensure_voice_exists, get_voices, find_voice
import sys

try:
    print('  Getting voice list...')
    voices = get_voices('$MODELS_DIR', update_voices=True)

    if '$VOICE_MODEL' not in voices:
        print('  Voice not found in repository!')
        sys.exit(1)

    print('  Downloading voice files...')
    ensure_voice_exists('$VOICE_MODEL', '$MODELS_DIR', voices)

    print('  ✓ Voice model downloaded successfully')
except Exception as e:
    print(f'  ✗ Error: {e}')
    sys.exit(1)
"@

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Voice model ready" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ Voice will be downloaded on first use" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "  ⚠ Pre-download failed, but voice will download on first use" -ForegroundColor Yellow
}

# Step 5: Test TTS
Write-Host "`n[5/5] Testing TTS..." -ForegroundColor Yellow

python -c @"
from piper import PiperVoice
from piper.download import ensure_voice_exists, get_voices, find_voice
import sys

try:
    print('  Loading voice...')
    voices = get_voices('$MODELS_DIR', update_voices=True)

    # Ensure voice exists
    ensure_voice_exists('$VOICE_MODEL', '$MODELS_DIR', voices)

    # Find voice
    voice_info = find_voice('$VOICE_MODEL', '$MODELS_DIR')

    # Load voice
    voice = PiperVoice.load(voice_info['model_path'], config_path=voice_info.get('config_path'))

    print('  Synthesizing test message...')
    test_text = 'Hello, I am Val, your virtual assistant. Piper TTS is working correctly.'

    # Synthesize
    audio_chunks = []
    for chunk in voice.synthesize_stream_raw(test_text):
        audio_chunks.append(chunk)

    if audio_chunks:
        print('  ✓ TTS synthesis successful!')
        print(f'  ✓ Generated {len(audio_chunks)} audio chunks')
    else:
        print('  ✗ No audio generated')
        sys.exit(1)

except Exception as e:
    print(f'  ✗ TTS test failed: {e}')
    sys.exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ TTS test passed!" -ForegroundColor Green
}
else {
    Write-Host "  ✗ TTS test failed" -ForegroundColor Red
    Write-Host "  Please check the error messages above" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n==================================`n" -ForegroundColor Cyan
Write-Host "✓ Piper TTS Setup Complete!" -ForegroundColor Green
Write-Host "`nConfiguration:" -ForegroundColor White
Write-Host "  Voice Model:  $VOICE_MODEL" -ForegroundColor Gray
Write-Host "  Models Dir:   $MODELS_DIR" -ForegroundColor Gray
Write-Host "  Config File:  $VOICE_CONFIG" -ForegroundColor Gray

Write-Host "`nNext Steps:" -ForegroundColor White
Write-Host "  1. The default voice (lessac) is ready to use" -ForegroundColor Gray
Write-Host "  2. You can change the voice in $VOICE_CONFIG" -ForegroundColor Gray
Write-Host "  3. Available voices: en_US-amy, en_US-ryan, en_GB-alan, and more" -ForegroundColor Gray
Write-Host "  4. Run main_client.py to start using Val with TTS" -ForegroundColor Gray

Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
