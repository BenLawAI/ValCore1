#Requires -RunAsAdministrator

# VALCORE1 Voice Embeddings Creation
# Creates voice embeddings from recorded samples using Resemblyzer

$ErrorActionPreference = "Stop"

Write-Host "`n=== VALCORE1 Voice Embeddings Creation ===" -ForegroundColor Cyan
Write-Host "This script will create voice embeddings from your recorded samples`n"

# Check dependencies
$depsTest = @"
import sys
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    from pathlib import Path
    import numpy as np
    print('DEPS_OK')
except ImportError as e:
    print(f'MISSING:{e}')
    sys.exit(1)
"@

$result = python -c $depsTest 2>&1

if ($result -ne "DEPS_OK") {
    Write-Host "ERROR: Resemblyzer not installed" -ForegroundColor Red
    Write-Host "Install with: pip install resemblyzer`n" -ForegroundColor Yellow
    exit 1
}

# Load voice profile config
$configPath = "A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\voice_profile_config.json"

if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Voice profile config not found: $configPath" -ForegroundColor Red
    Write-Host "Please run 2_record_voice_profile.ps1 first`n" -ForegroundColor Yellow
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json

Write-Host "Speaker: $($config.speaker_name)" -ForegroundColor Cyan
Write-Host "Samples directory: $($config.samples_directory)" -ForegroundColor Cyan
Write-Host "Sample count: $($config.sample_count)`n" -ForegroundColor Cyan

# Check for samples
$samples = Get-ChildItem -Path $config.samples_directory -Filter "*.wav"

if ($samples.Count -eq 0) {
    Write-Host "ERROR: No audio samples found in $($config.samples_directory)" -ForegroundColor Red
    Write-Host "Please run 2_record_voice_profile.ps1 first`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found $($samples.Count) audio samples" -ForegroundColor Green
Write-Host "`nCreating voice embeddings...`n" -ForegroundColor Yellow

# Embeddings creation script
$embeddingsScript = @"
import sys
from pathlib import Path
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

try:
    print('Initializing voice encoder...')
    encoder = VoiceEncoder()

    # Load samples
    samples_dir = Path('$($config.samples_directory.Replace('\', '/'))')
    wav_files = list(samples_dir.glob('*.wav'))

    print(f'Processing {len(wav_files)} audio files...')

    embeddings = []

    for i, wav_file in enumerate(wav_files, 1):
        try:
            # Preprocess audio
            wav = preprocess_wav(wav_file)

            # Create embedding
            embedding = encoder.embed_utterance(wav)

            embeddings.append(embedding)

            print(f'  [{i}/{len(wav_files)}] Processed: {wav_file.name}')

        except Exception as e:
            print(f'  WARNING: Failed to process {wav_file.name}: {e}')

    if len(embeddings) == 0:
        print('ERROR: No embeddings created')
        sys.exit(1)

    # Convert to numpy array
    embeddings_array = np.array(embeddings)

    print(f'\nCreated {len(embeddings)} embeddings')
    print(f'Embedding shape: {embeddings_array.shape}')

    # Calculate mean embedding (speaker profile)
    mean_embedding = np.mean(embeddings_array, axis=0)

    print(f'Mean embedding shape: {mean_embedding.shape}')

    # Save embeddings
    output_path = samples_dir / 'embeddings.npy'
    np.save(output_path, embeddings_array)
    print(f'\nSaved all embeddings: {output_path}')

    # Save mean embedding (this is the speaker profile)
    mean_output_path = samples_dir / 'speaker_embedding.npy'
    np.save(mean_output_path, mean_embedding)
    print(f'Saved speaker profile: {mean_output_path}')

    # Calculate statistics
    std_embedding = np.std(embeddings_array, axis=0)
    mean_std = np.mean(std_embedding)

    print(f'\nEmbedding statistics:')
    print(f'  Mean std dev: {mean_std:.6f}')

    if mean_std < 0.05:
        print('  Consistency: Excellent')
    elif mean_std < 0.1:
        print('  Consistency: Good')
    else:
        print('  Consistency: Fair (consider re-recording some samples)')

    print('\nEMBEDDINGS_OK')
    sys.exit(0)

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

# Run embeddings creation
try {
    $embeddingsResult = python -c $embeddingsScript 2>&1

    Write-Host $embeddingsResult -ForegroundColor White

    if ($embeddingsResult -contains "EMBEDDINGS_OK") {
        Write-Host "`n=== Embeddings Created Successfully ===" -ForegroundColor Green
    } else {
        throw "Embeddings creation failed"
    }
} catch {
    Write-Host "`nERROR: Failed to create embeddings: $_" -ForegroundColor Red
    exit 1
}

# Update configuration
$config.embeddings_file = "$($config.samples_directory)\speaker_embedding.npy"

try {
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "Configuration updated: $configPath" -ForegroundColor Green
} catch {
    Write-Host "WARN: Could not update configuration: $_" -ForegroundColor Yellow
}

# Verify embeddings files
$embeddingsFile = "$($config.samples_directory)\embeddings.npy"
$speakerProfileFile = "$($config.samples_directory)\speaker_embedding.npy"

if ((Test-Path $embeddingsFile) -and (Test-Path $speakerProfileFile)) {
    Write-Host "`nEmbeddings files created:" -ForegroundColor Cyan
    Write-Host "  All embeddings: $embeddingsFile" -ForegroundColor White
    Write-Host "  Speaker profile: $speakerProfileFile" -ForegroundColor White
} else {
    Write-Host "`nWARNING: Embeddings files not found" -ForegroundColor Yellow
}

# Next steps
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Run: 4_test_voice_verification.ps1" -ForegroundColor White
Write-Host "  2. This will test the speaker verification system" -ForegroundColor White
Write-Host "  3. Verify that your voice is correctly identified`n" -ForegroundColor White

exit 0
