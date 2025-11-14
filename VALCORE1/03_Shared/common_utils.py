"""
VALCORE1 Common Utilities
Shared utility functions used across components
"""

import uuid
import json
import re
import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

try:
    from .constants import *
    from .exceptions import *
except ImportError:
    # Fallback if constants/exceptions not yet imported
    PII_REDACTION_ENABLED = False
    PII_PATTERNS = []
    LOG_LEVEL_DEFAULT = "INFO"
    LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_MAX_SIZE_MB = 100
    LOG_BACKUP_COUNT = 5

logger = logging.getLogger(__name__)


def generate_event_id() -> str:
    """
    Generate unique event ID

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format (UTC)

    Returns:
        ISO format timestamp string (e.g., "2025-11-14T18:30:45.123456Z")
    """
    return datetime.now(timezone.utc).isoformat()


def get_timestamp_local() -> str:
    """
    Get current timestamp in local timezone

    Returns:
        ISO timestamp string
    """
    return datetime.now().isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse ISO timestamp string to datetime object

    Args:
        timestamp_str: ISO format timestamp

    Returns:
        datetime object

    Raises:
        ValueError: If timestamp format is invalid
    """
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def timestamp_to_filename() -> str:
    """
    Get timestamp suitable for filenames

    Returns:
        Timestamp string (e.g., "20251114_183045")
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_json_config(path: str) -> Dict:
    """
    Load and validate JSON configuration file

    Args:
        path: Path to JSON file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def save_json_config(path: str, data: Dict):
    """
    Save configuration to JSON file

    Args:
        path: Path to JSON file
        data: Data to save
    """
    config_path = Path(path)

    # Create parent directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(data, f, indent=2)


def sanitize_filename(name: str) -> str:
    """
    Remove invalid characters from filename

    Args:
        name: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)

    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    return sanitized


def calculate_token_count(text: str) -> int:
    """
    Approximate token count for text

    Uses simple heuristic: 4 characters ≈ 1 token

    Args:
        text: Text to count

    Returns:
        Estimated token count
    """
    return len(text) // 4


def format_bytes(size: int) -> str:
    """
    Format bytes as human-readable string

    Args:
        size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration as human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result or default
    """
    if denominator == 0:
        return default

    return numerator / denominator


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def validate_config_keys(config: Dict, required_keys: list) -> bool:
    """
    Validate that configuration has all required keys

    Args:
        config: Configuration dictionary
        required_keys: List of required key names

    Returns:
        True if all keys present

    Raises:
        ValueError: If keys are missing
    """
    missing_keys = [key for key in required_keys if key not in config]

    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    return True


# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def hash_text(text: str) -> str:
    """
    Generate SHA-256 hash of text

    Args:
        text: Input text

    Returns:
        Hex hash string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def hash_file(file_path: str) -> str:
    """
    Generate SHA-256 hash of file

    Args:
        file_path: Path to file

    Returns:
        Hex hash string

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_api_key(provided_key: str, expected_key: str) -> bool:
    """
    Verify API key using constant-time comparison

    Args:
        provided_key: API key provided by client
        expected_key: Expected API key

    Returns:
        True if keys match

    Note:
        Uses secrets.compare_digest for timing-attack resistance
    """
    return secrets.compare_digest(provided_key, expected_key)


def generate_api_key() -> str:
    """
    Generate secure API key

    Returns:
        Random API key (hex string, 64 characters)
    """
    return secrets.token_hex(32)


def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information from text

    Args:
        text: Input text with potential PII

    Returns:
        Text with PII redacted

    Example:
        redact_pii("SSN: 123-45-6789") -> "SSN: [REDACTED]"
    """
    if not PII_REDACTION_ENABLED:
        return text

    redacted = text

    for pattern in PII_PATTERNS:
        redacted = re.sub(pattern, "[REDACTED]", redacted)

    return redacted


# ============================================================================
# LOGGING UTILITIES
# ============================================================================

def setup_logging(
    name: str,
    log_file: Optional[str] = None,
    level: str = LOG_LEVEL_DEFAULT,
    enable_console: bool = True
) -> logging.Logger:
    """
    Set up logger with file and console handlers

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_console: Enable console output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_MAX_SIZE_MB * 1024 * 1024,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """
    Log exception with full traceback

    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context string
    """
    import traceback

    msg = f"{context}: {exc.__class__.__name__}: {str(exc)}" if context else str(exc)
    logger.error(msg)
    logger.debug("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))


# ============================================================================
# PATH/FILE UTILITIES
# ============================================================================

def ensure_directory(path: Path) -> Path:
    """
    Create directory if it doesn't exist

    Args:
        path: Directory path

    Returns:
        Path object

    Raises:
        PermissionError: If cannot create directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_project_root() -> Path:
    """
    Get VALCORE1 project root directory

    Returns:
        Path to project root
    """
    # Assuming this file is in VALCORE1/03_Shared/
    return Path(__file__).parent.parent


# ============================================================================
# SYSTEM UTILITIES
# ============================================================================

def check_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if network port is available

    Args:
        port: Port number
        host: Host address

    Returns:
        True if port is available
    """
    import socket

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind((host, port))
        return True
    except OSError:
        return False


def get_local_ip() -> str:
    """
    Get local IP address

    Returns:
        IP address string
    """
    import socket

    try:
        # Connect to external host (doesn't actually send data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def get_system_info() -> Dict[str, Any]:
    """
    Get system information

    Returns:
        Dictionary with system details
    """
    import platform
    try:
        import psutil
        has_psutil = True
    except ImportError:
        has_psutil = False

    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
    }

    if has_psutil:
        info.update({
            "cpu_count": psutil.cpu_count(),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
        })

    return info


def extract_command_intent(text: str) -> Optional[str]:
    """
    Extract command intent from user input

    Args:
        text: User command text

    Returns:
        Intent string or None

    Example:
        extract_command_intent("Hey Val, open notepad") -> "open"
    """
    text_lower = text.lower()

    # Command patterns
    patterns = {
        "open": r"open\s+(\w+)",
        "close": r"close",
        "switch": r"switch\s+to\s+(\w+)",
        "mic_off": r"(mic|microphone)\s+off",
        "mic_on": r"(mic|microphone)\s+on",
        "screenshot": r"(take\s+)?screenshot",
        "type": r"type\s+(this|that)",
        "undo": r"(undo|emergency\s+stop)",
        "status": r"status|how\s+are\s+you",
    }

    for intent, pattern in patterns.items():
        if re.search(pattern, text_lower):
            return intent

    return None
