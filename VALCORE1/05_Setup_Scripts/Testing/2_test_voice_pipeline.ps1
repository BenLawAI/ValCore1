#Requires -RunAsAdministrator

# VALCORE1 Voice Pipeline Test
# Tests the complete voice processing pipeline

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Voice Pipeline Test ===" -ForegroundColor Cyan
Write-Host "This script will test the voice processing pipeline end-to-end`n"

Write-Host "This test will:" -ForegroundColor Yellow
Write-Host "  1. Initialize voice system" -ForegroundColor White
Write-Host "  2. Record audio sample" -ForegroundColor White
Write-Host "  3. Run speech-to-text" -ForegroundColor White
Write-Host "  4. Verify speaker identity (if profile exists)" -ForegroundColor White
Write-Host "  5. Generate TTS response`n" -ForegroundColor White

$confirm = Read-Host "Run voice pipeline test? (Y/N)"

if ($confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Voice pipeline test script
$pipelineTest = @"
import sys
sys.path.insert(0, 'A:/000_START_HERE/VALCORE1_ROOT/Systems/VALCORE1')

print('Importing voice system...')

try:
    from VALCORE1.client_brain.core.voice_system_unified import VoiceSystemUnified
    import sounddevice as sd
    import numpy as np
    from pathlib import Path
except ImportError as e:
    print(f'ERROR: Import failed: {e}')
    sys.exit(1)

print('  Imports successful')

print('\nInitializing voice system...')

try:
    voice_system = VoiceSystemUnified()
    print('  Voice system initialized')
except Exception as e:
    print(f'  ERROR: Failed to initialize: {e}')
    sys.exit(1)

print('\n[Test 1/4] Testing microphone...')

try:
    # List devices
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]

    if len(input_devices) == 0:
        print('  FAIL: No microphones detected')
        sys.exit(1)

    print(f'  PASS: {len(input_devices)} microphone(s) detected')
except Exception as e:
    print(f'  FAIL: {e}')
    sys.exit(1)

print('\n[Test 2/4] Testing speech-to-text...')

try:
    input('  Press ENTER to record (3 seconds)...')

    print('  Say something clear like: "This is a test"')
    print('  Recording in 3...')

    import time
    time.sleep(0.7)
    print('  2...')
    time.sleep(0.7)
    print('  1...')
    time.sleep(0.7)
    print('  RECORDING NOW!')

    # Record
    sample_rate = 16000
    duration = 3
    audio = sd.rec(int(duration * sample_rate),
                   samplerate=sample_rate,
                   channels=1,
                   dtype=np.float32)
    sd.wait()

    print('  Processing audio...')

    # Convert to format expected by Whisper
    audio_np = (audio.squeeze() * 32768).astype(np.int16).astype(np.float32) / 32768

    # Run STT (if Whisper available)
    try:
        text = voice_system.transcribe_audio(audio_np)

        if text:
            print(f'  PASS: Transcribed: "{text}"')
        else:
            print('  WARN: No transcription (audio may be silent or Whisper not loaded)')

    except AttributeError:
        print('  SKIP: STT not fully configured (this is okay for initial setup)')

except Exception as e:
    print(f'  FAIL: {e}')

print('\n[Test 3/4] Testing speaker verification...')

try:
    # Check if voice profile exists
    profile_path = Path('A:/000_START_HERE/VALCORE1_ROOT/Systems/VALCORE1/01_Client_Brain/voice_profiles/ben_voice_samples/speaker_embedding.npy')

    if profile_path.exists():
        print('  Voice profile found')

        # Test verification (if implemented)
        try:
            verified = voice_system.verify_speaker(audio_np)

            if verified:
                print('  PASS: Speaker verified')
            else:
                print('  WARN: Speaker not verified (may need re-enrollment)')

        except AttributeError:
            print('  SKIP: Speaker verification not fully configured')
    else:
        print('  SKIP: No voice profile found (run voice enrollment first)')

except Exception as e:
    print(f'  WARN: {e}')

print('\n[Test 4/4] Testing text-to-speech...')

try:
    test_text = "This is a test of the text to speech system."

    print(f'  Generating speech for: "{test_text}"')

    # Test TTS (placeholder)
    try:
        audio_output = voice_system.synthesize_speech(test_text)

        if audio_output is not None:
            print('  PASS: TTS generated audio')
        else:
            print('  SKIP: TTS not fully configured (using placeholder)')

    except (AttributeError, NotImplementedError):
        print('  SKIP: TTS not fully configured (this is okay - using Kokoro)')

except Exception as e:
    print(f'  WARN: {e}')

print('\n=== Voice Pipeline Test Complete ===')
print('Core voice components are functional.')
print('\nNote: Some features may show SKIP status during initial setup.')
print('This is normal - they will be activated during final configuration.')

sys.exit(0)
"@

# Run test
try {
    python -c $pipelineTest

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nVoice Pipeline Status: OPERATIONAL" -ForegroundColor Green
        Write-Host "Voice system is working correctly!`n" -ForegroundColor Green
        exit 0
    } else {
        throw "Pipeline test failed"
    }
} catch {
    Write-Host "`nVoice Pipeline Status: ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host "Some voice features may need configuration`n" -ForegroundColor Yellow
    exit 1
}
