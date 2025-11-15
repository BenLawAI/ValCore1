"""
Unit tests for VALVoiceSystem
Tests TTS, STT, wake word, and speaker verification
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import json
from pathlib import Path


class TestVoiceSystemTTS(unittest.TestCase):
    """Test TTS functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock config
        self.test_config = {
            "audio": {
                "sample_rate": 16000,
                "chunk_size": 512,
                "channels": 1,
                "use_default_device": True
            },
            "stt": {
                "model": "base",
                "compute_type": "float32",
                "beam_size": 5,
                "vad_filter": True
            },
            "tts": {
                "rate": 150,
                "volume": 0.9,
                "voice_id": None
            },
            "wake_word": {
                "access_key": "",
                "sensitivity": 0.5
            },
            "speaker_verification": {
                "enabled": False,
                "profiles_dir": "config/voice_profiles",
                "threshold": 0.7
            }
        }

        # Create temporary config file
        self.config_file = Path("test_voice_config.json")
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up test artifacts"""
        if self.config_file.exists():
            self.config_file.unlink()

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.pyttsx3')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.WhisperModel')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.torch')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.pyaudio')
    def test_tts_initialization_pyttsx3(self, mock_pyaudio, mock_torch, mock_whisper, mock_pyttsx3, mock_syspath):
        """Test TTS initializes with pyttsx3"""
        # Mock CUDA availability
        mock_torch.cuda.is_available.return_value = False

        # Mock pyttsx3
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        # Import after mocking
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.voice_system_unified import VALVoiceSystem

        # Create voice system
        vs = VALVoiceSystem(config_path=str(self.config_file))

        # Verify TTS was initialized
        self.assertTrue(vs.tts_available)
        self.assertEqual(vs.tts_backend, "pyttsx3")
        mock_engine.setProperty.assert_any_call('rate', 150)
        mock_engine.setProperty.assert_any_call('volume', 0.9)

    @patch('sys.path')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.pyttsx3')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.WhisperModel')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.torch')
    @patch('VALCORE1.01_Client_Brain.core.voice_system_unified.pyaudio')
    def test_speak_method(self, mock_pyaudio, mock_torch, mock_whisper, mock_pyttsx3, mock_syspath):
        """Test speak() method works correctly"""
        # Setup mocks
        mock_torch.cuda.is_available.return_value = False
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine

        # Import and create system
        import sys
        sys.path.insert(0, '/home/user/ValCore1/VALCORE1')
        from VALCORE1.01_Client_Brain.core.voice_system_unified import VALVoiceSystem

        vs = VALVoiceSystem(config_path=str(self.config_file))

        # Test speak
        vs.speak("Hello world", blocking=True)

        # Verify TTS engine was called
        mock_engine.say.assert_called_once_with("Hello world")
        mock_engine.runAndWait.assert_called()


class TestVoiceSystemSTT(unittest.TestCase):
    """Test STT functionality"""

    def test_transcribe_audio(self):
        """Test audio transcription"""
        # This would require actual Whisper model - placeholder for now
        pass


class TestVoiceSystemWakeWord(unittest.TestCase):
    """Test wake word detection"""

    def test_wake_word_detection(self):
        """Test wake word detection"""
        # This would require Porcupine - placeholder for now
        pass


class TestVoiceSystemSpeakerVerification(unittest.TestCase):
    """Test speaker verification"""

    def test_speaker_verification(self):
        """Test speaker verification"""
        # This would require Resemblyzer - placeholder for now
        pass


if __name__ == '__main__':
    unittest.main()
