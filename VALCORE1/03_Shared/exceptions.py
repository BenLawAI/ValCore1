"""
VALCORE1 Custom Exceptions
Provides specific exception types for better error handling and debugging
"""


class VALCoreException(Exception):
    """Base exception for all VALCORE1 errors"""
    pass


# ============================================================================
# VOICE SYSTEM EXCEPTIONS
# ============================================================================

class VoiceSystemException(VALCoreException):
    """Base exception for voice system errors"""
    pass


class MicrophoneException(VoiceSystemException):
    """Microphone not available or failed to initialize"""
    pass


class STTException(VoiceSystemException):
    """Speech-to-text transcription failed"""
    pass


class TTSException(VoiceSystemException):
    """Text-to-speech synthesis failed"""
    pass


class WakeWordException(VoiceSystemException):
    """Wake word detection failed or not available"""
    pass


class SpeakerVerificationException(VoiceSystemException):
    """Speaker verification failed or not available"""
    pass


class SpeakerVerificationFailure(VoiceSystemException):
    """Speaker did not match expected voice profile"""
    pass


class AudioDeviceException(VoiceSystemException):
    """Audio device error (input/output)"""
    pass


# ============================================================================
# NETWORK/SERVER EXCEPTIONS
# ============================================================================

class NetworkException(VALCoreException):
    """Base exception for network-related errors"""
    pass


class ServerUnavailableException(NetworkException):
    """ATOM server is not reachable"""
    pass


class ServerTimeoutException(NetworkException):
    """Server request timed out"""
    pass


class ServerAuthenticationException(NetworkException):
    """Server authentication failed"""
    pass


class FallbackUnavailableException(NetworkException):
    """Both server and fallback LLM are unavailable"""
    pass


class ConnectionRetryExhaustedException(NetworkException):
    """All connection retry attempts failed"""
    pass


# ============================================================================
# LLM EXCEPTIONS
# ============================================================================

class LLMException(VALCoreException):
    """Base exception for LLM-related errors"""
    pass


class ModelNotLoadedException(LLMException):
    """LLM model failed to load or not available"""
    pass


class GenerationException(LLMException):
    """LLM generation/inference failed"""
    pass


class ContextWindowExceededException(LLMException):
    """Input exceeds model's context window"""
    pass


class ModelNotFoundException(LLMException):
    """Requested model not found on system"""
    pass


# ============================================================================
# AUTOMATION EXCEPTIONS
# ============================================================================

class AutomationException(VALCoreException):
    """Base exception for automation errors"""
    pass


class SecurityViolationException(AutomationException):
    """Attempted to perform disallowed automation action"""
    pass


class WindowNotFoundException(AutomationException):
    """Target window not found"""
    pass


class ApplicationLaunchException(AutomationException):
    """Failed to launch application"""
    pass


class UndoException(AutomationException):
    """Emergency undo operation failed"""
    pass


# ============================================================================
# CONFIGURATION EXCEPTIONS
# ============================================================================

class ConfigurationException(VALCoreException):
    """Base exception for configuration errors"""
    pass


class ConfigFileNotFoundException(ConfigurationException):
    """Configuration file not found"""
    pass


class ConfigValidationException(ConfigurationException):
    """Configuration validation failed"""
    pass


class InvalidConfigValueException(ConfigurationException):
    """Configuration contains invalid value"""
    pass


class MissingConfigKeyException(ConfigurationException):
    """Required configuration key missing"""
    pass


# ============================================================================
# GPU/HARDWARE EXCEPTIONS
# ============================================================================

class HardwareException(VALCoreException):
    """Base exception for hardware-related errors"""
    pass


class GPUNotFoundException(HardwareException):
    """Expected GPU not found"""
    pass


class GPUMemoryException(HardwareException):
    """GPU out of memory or memory allocation failed"""
    pass


class CUDAException(HardwareException):
    """CUDA-related error"""
    pass


class GPUTemperatureException(HardwareException):
    """GPU temperature exceeds safe threshold"""
    pass


# ============================================================================
# LIBRARY/MEMORY EXCEPTIONS
# ============================================================================

class LibraryException(VALCoreException):
    """Base exception for library/memory system errors"""
    pass


class MemoryCompressionException(LibraryException):
    """Memory compression failed"""
    pass


class SearchException(LibraryException):
    """Semantic search failed"""
    pass


class IndexException(LibraryException):
    """FAISS index operation failed"""
    pass


class ConversationNotFoundException(LibraryException):
    """Requested conversation not found"""
    pass


# ============================================================================
# ROOM/CONTEXT EXCEPTIONS
# ============================================================================

class RoomException(VALCoreException):
    """Base exception for room management errors"""
    pass


class RoomNotFoundException(RoomException):
    """Requested room context not found"""
    pass


class RoomSwitchException(RoomException):
    """Failed to switch room context"""
    pass


class InvalidRoomConfigException(RoomException):
    """Room configuration is invalid"""
    pass


# ============================================================================
# SECURITY EXCEPTIONS
# ============================================================================

class SecurityException(VALCoreException):
    """Base exception for security-related errors"""
    pass


class AuthenticationException(SecurityException):
    """Authentication failed"""
    pass


class AuthorizationException(SecurityException):
    """User not authorized for requested action"""
    pass


class RateLimitException(SecurityException):
    """Rate limit exceeded"""
    pass


class InvalidAPIKeyException(SecurityException):
    """API key is invalid or expired"""
    pass


# ============================================================================
# OFFLINE/SYNC EXCEPTIONS
# ============================================================================

class OfflineException(VALCoreException):
    """Base exception for offline mode errors"""
    pass


class QueueFullException(OfflineException):
    """Offline message queue is full"""
    pass


class SyncException(OfflineException):
    """Synchronization failed"""
    pass


class ConflictException(OfflineException):
    """Conflict detected during sync"""
    pass


# ============================================================================
# SYSTEM EXCEPTIONS
# ============================================================================

class SystemException(VALCoreException):
    """Base exception for system-level errors"""
    pass


class InitializationException(SystemException):
    """Component initialization failed"""
    pass


class ShutdownException(SystemException):
    """Graceful shutdown failed"""
    pass


class EmergencyStopException(SystemException):
    """Emergency stop triggered"""
    pass


class HealthCheckException(SystemException):
    """Health check failed"""
    pass


class ResourceException(SystemException):
    """System resource exhausted (RAM, disk, etc.)"""
    pass


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================

class ValidationException(VALCoreException):
    """Base exception for validation errors"""
    pass


class InputValidationException(ValidationException):
    """User input validation failed"""
    pass


class MessageValidationException(ValidationException):
    """Message format validation failed"""
    pass


class SchemaValidationException(ValidationException):
    """Schema validation failed"""
    pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_exception_by_name(name: str) -> type:
    """
    Get exception class by name (for deserialization)

    Args:
        name: Exception class name

    Returns:
        Exception class

    Raises:
        ValueError: If exception name not found
    """
    exceptions_map = {
        cls.__name__: cls for cls in VALCoreException.__subclasses__()
    }

    # Also include nested subclasses
    for base_cls in VALCoreException.__subclasses__():
        for cls in base_cls.__subclasses__():
            exceptions_map[cls.__name__] = cls

    if name not in exceptions_map:
        raise ValueError(f"Exception '{name}' not found")

    return exceptions_map[name]


def format_exception_message(exc: Exception, include_trace: bool = False) -> str:
    """
    Format exception for user-friendly display

    Args:
        exc: Exception instance
        include_trace: Include stack trace

    Returns:
        Formatted error message
    """
    import traceback

    msg = f"[{exc.__class__.__name__}] {str(exc)}"

    if include_trace:
        msg += "\n\nStack trace:\n"
        msg += "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    return msg
