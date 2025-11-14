"""
Unit tests for custom exceptions
"""

import pytest
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "03_Shared"))

from exceptions import *


class TestExceptionHierarchy:
    """Test exception class hierarchy"""

    def test_base_exception(self):
        """Test base VALCORE1Exception"""
        exc = VALCORE1Exception("Test error")
        assert isinstance(exc, Exception)
        assert str(exc) == "Test error"

    def test_network_exceptions(self):
        """Test network exception hierarchy"""
        assert issubclass(NetworkException, VALCORE1Exception)
        assert issubclass(ServerConnectionError, NetworkException)
        assert issubclass(ServerTimeoutError, NetworkException)
        assert issubclass(AuthenticationError, NetworkException)
        assert issubclass(RateLimitError, NetworkException)

    def test_llm_exceptions(self):
        """Test LLM exception hierarchy"""
        assert issubclass(LLMException, VALCORE1Exception)
        assert issubclass(ModelNotFoundError, LLMException)
        assert issubclass(GenerationError, LLMException)
        assert issubclass(ModelLoadError, LLMException)

    def test_voice_exceptions(self):
        """Test voice exception hierarchy"""
        assert issubclass(VoiceException, VALCORE1Exception)
        assert issubclass(MicrophoneError, VoiceException)
        assert issubclass(WakeWordError, VoiceException)
        assert issubclass(STTError, VoiceException)
        assert issubclass(TTSError, VoiceException)
        assert issubclass(SpeakerVerificationError, VoiceException)

    def test_storage_exceptions(self):
        """Test storage exception hierarchy"""
        assert issubclass(StorageException, VALCORE1Exception)
        assert issubclass(LibraryError, StorageException)
        assert issubclass(IndexError, StorageException)
        assert issubclass(EncryptionError, StorageException)
        assert issubclass(BackupError, StorageException)

    def test_gpu_exceptions(self):
        """Test GPU exception hierarchy"""
        assert issubclass(GPUException, VALCORE1Exception)
        assert issubclass(GPUNotAvailableError, GPUException)
        assert issubclass(GPUOutOfMemoryError, GPUException)
        assert issubclass(CUDAError, GPUException)

    def test_room_exceptions(self):
        """Test room exception hierarchy"""
        assert issubclass(RoomException, VALCORE1Exception)
        assert issubclass(RoomNotFoundError, RoomException)
        assert issubclass(RoomConfigError, RoomException)

    def test_config_exceptions(self):
        """Test config exception hierarchy"""
        assert issubclass(ConfigException, VALCORE1Exception)
        assert issubclass(ConfigNotFoundError, ConfigException)
        assert issubclass(ConfigValidationError, ConfigException)

    def test_automation_exceptions(self):
        """Test automation exception hierarchy"""
        assert issubclass(AutomationException, VALCORE1Exception)
        assert issubclass(CommandExecutionError, AutomationException)
        assert issubclass(PermissionDeniedError, AutomationException)

    def test_health_exceptions(self):
        """Test health exception hierarchy"""
        assert issubclass(HealthException, VALCORE1Exception)
        assert issubclass(SystemOverloadError, HealthException)
        assert issubclass(TemperatureWarning, HealthException)

    def test_validation_exceptions(self):
        """Test validation exception hierarchy"""
        assert issubclass(ValidationException, VALCORE1Exception)
        assert issubclass(InputValidationError, ValidationException)
        assert issubclass(DataValidationError, ValidationException)

    def test_session_exceptions(self):
        """Test session exception hierarchy"""
        assert issubclass(SessionException, VALCORE1Exception)
        assert issubclass(SessionNotFoundError, SessionException)
        assert issubclass(SessionExpiredError, SessionException)


class TestExceptionRaising:
    """Test raising and catching exceptions"""

    def test_raise_specific_exception(self):
        """Test raising specific exception"""
        with pytest.raises(ServerConnectionError):
            raise ServerConnectionError("Cannot connect")

    def test_catch_specific_exception(self):
        """Test catching specific exception"""
        try:
            raise ModelNotFoundError("Model not found")
        except ModelNotFoundError as e:
            assert "Model not found" in str(e)

    def test_catch_base_exception(self):
        """Test catching via base exception"""
        try:
            raise InputValidationError("Invalid input")
        except VALCORE1Exception as e:
            assert isinstance(e, InputValidationError)

    def test_catch_parent_exception(self):
        """Test catching via parent exception"""
        try:
            raise STTError("Speech recognition failed")
        except VoiceException as e:
            assert isinstance(e, STTError)
