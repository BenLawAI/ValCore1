"""
VALCORE1 Common Utilities
Shared utility functions used across components
"""

import uuid
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def generate_event_id() -> str:
    """
    Generate unique event ID

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format

    Returns:
        ISO format timestamp string
    """
    return datetime.now().isoformat()


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
