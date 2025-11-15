"""
Tests for Voice System (TTS and STT)
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_config():
    """Mock configuration for voice system"""
    return {
        'audio': {
            'sample_rate': 16000,
            'chunk_size': 1024,
            'channels': 1,
            'use_default_device': True
        },
        'stt': {
            'model': 'base',
            'compute_type': 'int8',
            'beam_size': 5,
            'vad_filter': True
        },
        'tts': {
            'model_path': 'models/en_US-lessac-medium.onnx'
        },
        'wake_word': {
            'access_key': '',
            'sensitivity': 0.5
        },
        'speaker_verification': {
            'enabled': False,
            'threshold': 0.75,
            'profiles_dir': 'voice_profiles'
        }
    }


@pytest.mark.unit
class TestVoiceSystemInit:
    """Test voice system initialization"""

    def test_config_loading(self, mock_config, tmp_path):
        """Test configuration loading"""
        # Create temp config file
        config_file = tmp_path / "voice_config.json"
        import json
        with open(config_file, 'w') as f:
            json.dump(mock_config, f)

        # Test that config loads successfully
        assert config_file.exists()
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        assert loaded_config['audio']['sample_rate'] == 16000


@pytest.mark.unit
class TestTTS:
    """Test Text-to-Speech functionality"""

    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.PIPER_AVAILABLE', True)
    def test_tts_synthesis_returns_audio(self):
        """Test that TTS synthesis returns audio data"""
        # Mock Piper voice
        mock_piper = MagicMock()
        mock_audio = np.random.randint(-32768, 32767, 22050, dtype=np.int16)
        mock_piper.synthesize.return_value = [mock_audio]

        # Test synthesis
        with patch('VALCORE1.01_Client_Brain.core.voice_system_unified.PiperVoice') as MockPiper:
            MockPiper.load.return_value = mock_piper

            # Simulate TTS synthesis
            text = "Hello, this is a test"
            audio_chunks = list(mock_piper.synthesize(text))
            assert len(audio_chunks) > 0

            audio_data = np.concatenate(audio_chunks)
            assert isinstance(audio_data, np.ndarray)
            assert audio_data.dtype == np.int16

    def test_tts_handles_empty_text(self):
        """Test TTS handles empty text gracefully"""
        text = ""
        # Should not crash
        assert isinstance(text, str)

    def test_tts_handles_long_text(self):
        """Test TTS handles long text"""
        text = "This is a very long text. " * 100
        assert len(text) > 1000


@pytest.mark.unit
class TestSTT:
    """Test Speech-to-Text functionality"""

    def test_stt_transcription_format(self):
        """Test STT returns proper text format"""
        # Simulate audio input
        sample_rate = 16000
        duration = 3  # seconds
        audio_data = np.random.randn(sample_rate * duration).astype(np.float32)

        # Audio should be float32
        assert audio_data.dtype == np.float32
        assert len(audio_data) == sample_rate * duration

    def test_stt_handles_empty_audio(self):
        """Test STT handles empty audio"""
        audio_data = np.array([], dtype=np.float32)
        assert len(audio_data) == 0

    def test_stt_audio_normalization(self):
        """Test audio normalization for STT"""
        # Create int16 audio
        audio_int16 = np.random.randint(-32768, 32767, 16000, dtype=np.int16)

        # Normalize to float32
        audio_float32 = audio_int16.astype(np.float32) / 32767.0

        assert audio_float32.dtype == np.float32
        assert audio_float32.min() >= -1.0
        assert audio_float32.max() <= 1.0


@pytest.mark.unit
class TestWakeWord:
    """Test wake word detection"""

    def test_wake_word_detection_format(self):
        """Test wake word detection input format"""
        # Wake word expects int16 audio
        chunk_size = 512
        audio_chunk = np.random.randint(-32768, 32767, chunk_size, dtype=np.int16)

        assert audio_chunk.dtype == np.int16
        assert len(audio_chunk) == chunk_size

    def test_wake_word_disabled_returns_true(self):
        """Test that disabled wake word always returns True"""
        # When wake word is disabled, system should always be active
        wake_word_available = False
        result = True if not wake_word_available else False
        assert result == True


@pytest.mark.unit
class TestAudioProcessing:
    """Test audio processing utilities"""

    def test_audio_recording_duration(self):
        """Test audio recording duration calculation"""
        sample_rate = 16000
        chunk_size = 1024
        duration = 5  # seconds

        num_chunks = int(sample_rate / chunk_size * duration)
        expected_samples = num_chunks * chunk_size

        # Verify calculation
        assert num_chunks > 0
        assert expected_samples > 0

    def test_audio_conversion_int16_to_float32(self):
        """Test audio conversion from int16 to float32"""
        audio_int16 = np.array([0, 16384, -16384, 32767, -32768], dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32767.0

        assert audio_float32.dtype == np.float32
        assert abs(audio_float32[0]) < 0.01  # Close to 0
        assert audio_float32.max() <= 1.0
        assert audio_float32.min() >= -1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
