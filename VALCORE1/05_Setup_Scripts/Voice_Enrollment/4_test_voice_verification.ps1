#Requires -RunAsAdministrator

# VALCORE1 Voice Verification Test
# Tests speaker verification using recorded voice profile

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Voice Verification Test ===" -ForegroundColor Cyan
Write-Host "This script will test speaker verification with your voice profile`n"

# Check dependencies
$depsTest = @"
import sys
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    import sounddevice as sd
    import numpy as np
    import wave
    print('DEPS_OK')
except ImportError as e:
    print(f'MISSING:{e}')
    sys.exit(1)
"@

$result = python -c $depsTest 2>&1

if ($result -ne "DEPS_OK") {
    Write-Host "ERROR: Required libraries not installed" -ForegroundColor Red
    Write-Host "Install with: pip install resemblyzer sounddevice numpy`n" -ForegroundColor Yellow
    exit 1
}

# Load voice profile config
$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\voice_profile_config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Voice profile config not found: $configPath" -ForegroundColor Red
    Write-Host "Please run voice enrollment scripts first`n" -ForegroundColor Yellow
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json

# Check speaker profile exists
$speakerProfilePath = "$($config.samples_directory)\speaker_embedding.npy"

if (-not (Test-Path $speakerProfilePath)) {
    Write-Host "ERROR: Speaker profile not found: $speakerProfilePath" -ForegroundColor Red
    Write-Host "Please run 3_create_voice_embeddings.ps1 first`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "Speaker: $($config.speaker_name)" -ForegroundColor Cyan
Write-Host "Profile: $speakerProfilePath`n" -ForegroundColor Cyan

Write-Host "This test will:" -ForegroundColor Yellow
Write-Host "  1. Record your voice (3 seconds)" -ForegroundColor White
Write-Host "  2. Create embedding from recording" -ForegroundColor White
Write-Host "  3. Compare with stored voice profile" -ForegroundColor White
Write-Host "  4. Calculate similarity score`n" -ForegroundColor White

$confirm = Read-Host "Ready to test? (Y/N)"

if ($confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Test phrases
$testPhrases = @(
    "Hey Val, what time is it?",
    "Val, tell me about my schedule",
    "Okay Val, what's the weather today?"
)

Write-Host "`nYou will say 3 test phrases to verify your voice`n" -ForegroundColor Cyan

# Verification test script
$verificationScript = @"
import sys
import sounddevice as sd
import numpy as np
import wave
from pathlib import Path
from resemblyzer import VoiceEncoder, preprocess_wav
import tempfile

def record_audio(duration=3.0, sample_rate=16000):
    '''Record audio sample'''
    audio = sd.rec(int(duration * sample_rate),
                  samplerate=sample_rate,
                  channels=1,
                  dtype=np.float32)
    sd.wait()
    return audio, sample_rate

def save_wav(audio, sample_rate, output_path):
    '''Save audio as WAV'''
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(output_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

def verify_speaker(test_wav_path, speaker_profile_path, encoder):
    '''Verify if test audio matches speaker profile'''
    try:
        # Load speaker profile
        speaker_embedding = np.load(speaker_profile_path)

        # Process test audio
        test_wav = preprocess_wav(test_wav_path)
        test_embedding = encoder.embed_utterance(test_wav)

        # Calculate cosine similarity
        similarity = np.dot(speaker_embedding, test_embedding)
        similarity = float(similarity)

        return similarity

    except Exception as e:
        print(f'Verification error: {e}')
        return 0.0

# Initialize
print('Initializing voice encoder...')
encoder = VoiceEncoder()

speaker_profile_path = Path('$($speakerProfilePath.Replace('\', '/'))')

test_phrases = [
    '$($testPhrases[0])',
    '$($testPhrases[1])',
    '$($testPhrases[2])'
]

similarities = []

for i, phrase in enumerate(test_phrases, 1):
    print(f'\n[Test {i}/3]')
    input('Press ENTER when ready...')

    print(f'Say: "{phrase}"')
    print('Recording in 3...')

    import time
    time.sleep(0.7)
    print('2...')
    time.sleep(0.7)
    print('1...')
    time.sleep(0.7)
    print('RECORDING NOW!', flush=True)

    # Record
    audio, sample_rate = record_audio(duration=3.0)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        temp_path = tmp.name
        save_wav(audio, sample_rate, temp_path)

        # Verify
        similarity = verify_speaker(temp_path, speaker_profile_path, encoder)

        similarities.append(similarity)

        print(f'\nSimilarity score: {similarity:.4f}')

        if similarity > 0.75:
            print('  Result: VERIFIED (High confidence)', flush=True)
        elif similarity > 0.65:
            print('  Result: VERIFIED (Medium confidence)', flush=True)
        elif similarity > 0.55:
            print('  Result: POSSIBLE (Low confidence)', flush=True)
        else:
            print('  Result: NOT VERIFIED (Speaker mismatch)', flush=True)

    # Clean up
    import os
    os.unlink(temp_path)

# Summary
print('\n=== Verification Summary ===')
print(f'Tests completed: {len(similarities)}')
print(f'Average similarity: {np.mean(similarities):.4f}')
print(f'Min similarity: {np.min(similarities):.4f}')
print(f'Max similarity: {np.max(similarities):.4f}')

avg_similarity = np.mean(similarities)

if avg_similarity > 0.75:
    print('\nVoice Profile Quality: EXCELLENT')
    print('Your voice will be reliably verified by VALCORE1')
elif avg_similarity > 0.65:
    print('\nVoice Profile Quality: GOOD')
    print('Your voice should be verified with good accuracy')
elif avg_similarity > 0.55:
    print('\nVoice Profile Quality: FAIR')
    print('Consider re-recording voice profile for better accuracy')
else:
    print('\nVoice Profile Quality: POOR')
    print('Please re-record your voice profile')

print('\nTEST_COMPLETE')
"@

# Run verification test
try {
    $testResult = python -c $verificationScript 2>&1

    Write-Host $testResult -ForegroundColor White

    if ($testResult -contains "TEST_COMPLETE") {
        Write-Host "`n=== Test Complete ===" -ForegroundColor Green
    } else {
        throw "Test failed"
    }
} catch {
    Write-Host "`nERROR: Verification test failed: $_" -ForegroundColor Red
    exit 1
}

# Recommendations
Write-Host "`nRecommendations:" -ForegroundColor Cyan
Write-Host "  - Similarity > 0.75: Excellent - no action needed" -ForegroundColor Green
Write-Host "  - Similarity 0.65-0.75: Good - may work well" -ForegroundColor Yellow
Write-Host "  - Similarity < 0.65: Re-record voice profile recommended" -ForegroundColor Red

Write-Host "`nVoice verification testing complete!" -ForegroundColor Green
Write-Host "VALCORE1 is ready to verify your voice.`n" -ForegroundColor Green

exit 0
