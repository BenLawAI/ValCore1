"""
VALCORE1 Custom Exception Types
Provides specific exception types for better error handling and debugging
"""


# Base Exception
class VALCORE1Exception(Exception):
    """Base exception for all VALCORE1 errors"""
    pass


# Network Exceptions
class NetworkException(VALCORE1Exception):
    """Base class for network-related errors"""
    pass


class ServerConnectionError(NetworkException):
    """Failed to connect to server"""
    pass


class ServerTimeoutError(NetworkException):
    """Server request timed out"""
    pass


class AuthenticationError(NetworkException):
    """Authentication failed"""
    pass


class RateLimitError(NetworkException):
    """Rate limit exceeded"""
    pass


class TLSError(NetworkException):
    """TLS/SSL error"""
    pass


# LLM Exceptions
class LLMException(VALCORE1Exception):
    """Base class for LLM-related errors"""
    pass


class ModelNotFoundError(LLMException):
    """LLM model not found"""
    pass


class GenerationError(LLMException):
    """Error during text generation"""
    pass


class ModelLoadError(LLMException):
    """Failed to load model"""
    pass


# Voice System Exceptions
class VoiceException(VALCORE1Exception):
    """Base class for voice-related errors"""
    pass


class MicrophoneError(VoiceException):
    """Microphone access error"""
    pass


class WakeWordError(VoiceException):
    """Wake word detection error"""
    pass


class STTError(VoiceException):
    """Speech-to-text error"""
    pass


class TTSError(VoiceException):
    """Text-to-speech error"""
    pass


class SpeakerVerificationError(VoiceException):
    """Speaker verification failed"""
    pass


# Storage Exceptions
class StorageException(VALCORE1Exception):
    """Base class for storage-related errors"""
    pass


class LibraryError(StorageException):
    """Library/database error"""
    pass


class IndexError(StorageException):
    """FAISS index error"""
    pass


class EncryptionError(StorageException):
    """Data encryption/decryption error"""
    pass


class BackupError(StorageException):
    """Backup operation failed"""
    pass


# GPU Exceptions
class GPUException(VALCORE1Exception):
    """Base class for GPU-related errors"""
    pass


class GPUNotAvailableError(GPUException):
    """GPU not available"""
    pass


class GPUOutOfMemoryError(GPUException):
    """GPU out of memory"""
    pass


class CUDAError(GPUException):
    """CUDA error"""
    pass


# Room Management Exceptions
class RoomException(VALCORE1Exception):
    """Base class for room-related errors"""
    pass


class RoomNotFoundError(RoomException):
    """Room not found"""
    pass


class RoomConfigError(RoomException):
    """Room configuration error"""
    pass


# Configuration Exceptions
class ConfigException(VALCORE1Exception):
    """Base class for configuration errors"""
    pass


class ConfigNotFoundError(ConfigException):
    """Configuration file not found"""
    pass


class ConfigValidationError(ConfigException):
    """Configuration validation failed"""
    pass


# Automation Exceptions
class AutomationException(VALCORE1Exception):
    """Base class for automation errors"""
    pass


class CommandExecutionError(AutomationException):
    """Failed to execute automation command"""
    pass


class PermissionDeniedError(AutomationException):
    """Insufficient permissions for operation"""
    pass


# Health Monitoring Exceptions
class HealthException(VALCORE1Exception):
    """Base class for health monitoring errors"""
    pass


class SystemOverloadError(HealthException):
    """System resources overloaded"""
    pass


class TemperatureWarning(HealthException):
    """GPU/CPU temperature too high"""
    pass


# Validation Exceptions
class ValidationException(VALCORE1Exception):
    """Base class for validation errors"""
    pass


class InputValidationError(ValidationException):
    """Input validation failed"""
    pass


class DataValidationError(ValidationException):
    """Data validation failed"""
    pass


# Session Exceptions
class SessionException(VALCORE1Exception):
    """Base class for session errors"""
    pass


class SessionNotFoundError(SessionException):
    """Session not found"""
    pass


class SessionExpiredError(SessionException):
    """Session expired"""
    pass
