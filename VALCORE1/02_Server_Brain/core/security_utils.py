"""
VALCORE1 Security Utilities
SSL/TLS certificate generation, input sanitization, and security helpers
"""

import os
import logging
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)


def generate_self_signed_cert(cert_dir: str = "certs") -> tuple:
    """
    Generate self-signed SSL certificate for HTTPS

    Args:
        cert_dir: Directory to store certificates

    Returns:
        Tuple of (cert_path, key_path)
    """
    try:
        from OpenSSL import crypto
    except ImportError:
        logger.error("pyOpenSSL not installed. Run: pip install pyOpenSSL")
        raise ImportError("pyOpenSSL required for certificate generation")

    # Create certs directory
    cert_path = Path(cert_dir)
    cert_path.mkdir(parents=True, exist_ok=True)

    cert_file = cert_path / "valcore1.crt"
    key_file = cert_path / "valcore1.key"

    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        logger.info(f"Using existing certificates: {cert_file}, {key_file}")
        return str(cert_file), str(key_file)

    logger.info("Generating self-signed SSL certificate...")

    # Create key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "VALCORE1"
    cert.get_subject().OU = "VALCORE1 Server"
    cert.get_subject().CN = "localhost"

    cert.set_serial_number(secrets.randbits(64))
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Valid for 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Write certificate and key
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # Set restrictive permissions on key file
    os.chmod(key_file, 0o600)

    logger.info(f"Certificate generated: {cert_file}")
    logger.info(f"Private key generated: {key_file}")
    logger.warning("Using self-signed certificate. For production, use a CA-signed certificate.")

    return str(cert_file), str(key_file)


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # Truncate to max length
    text = text[:max_length]

    # Remove null bytes
    text = text.replace('\x00', '')

    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char == '\n' or char == '\t' or not char.isspace() or char == ' ')

    return text.strip()


def sanitize_json_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize JSON input data

    Args:
        data: Input dictionary

    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")

    sanitized = {}
    for key, value in data.items():
        # Sanitize keys
        if isinstance(key, str):
            key = sanitize_input(key, max_length=100)

        # Sanitize string values
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_json_input(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_input(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def validate_api_key(provided_key: str, stored_key: str) -> bool:
    """
    Securely compare API keys using constant-time comparison

    Args:
        provided_key: API key provided by client
        stored_key: Expected API key

    Returns:
        True if keys match, False otherwise
    """
    if not provided_key or not stored_key:
        return False

    return hmac.compare_digest(provided_key, stored_key)


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """
    Hash a password using PBKDF2

    Args:
        password: Password to hash
        salt: Optional salt (generated if not provided)

    Returns:
        Tuple of (hash, salt)
    """
    if salt is None:
        salt = os.urandom(32)

    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    return pwd_hash, salt


def verify_password(password: str, pwd_hash: bytes, salt: bytes) -> bool:
    """
    Verify a password against its hash

    Args:
        password: Password to verify
        pwd_hash: Stored password hash
        salt: Salt used for hashing

    Returns:
        True if password matches, False otherwise
    """
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(new_hash, pwd_hash)


def generate_api_key() -> str:
    """
    Generate a secure random API key

    Returns:
        Random API key string
    """
    return secrets.token_urlsafe(32)


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid, False otherwise
    """
    # Session ID should be alphanumeric and underscores, 1-64 characters
    pattern = r'^[a-zA-Z0-9_-]{1,64}$'
    return bool(re.match(pattern, session_id))


def validate_room_name(room_name: str) -> bool:
    """
    Validate room name format

    Args:
        room_name: Room name to validate

    Returns:
        True if valid, False otherwise
    """
    # Room name should be alphanumeric and underscores, 1-32 characters
    pattern = r'^[a-zA-Z0-9_]{1,32}$'
    return bool(re.match(pattern, room_name))


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed

        Args:
            identifier: Client identifier (IP, session ID, etc.)

        Returns:
            True if allowed, False if rate limit exceeded
        """
        now = datetime.now()

        # Initialize if new identifier
        if identifier not in self.requests:
            self.requests[identifier] = []

        # Remove old requests outside the window
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]

        # Check if limit exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

    def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests in current window

        Args:
            identifier: Client identifier

        Returns:
            Number of remaining requests
        """
        if identifier not in self.requests:
            return self.max_requests

        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        current_requests = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]

        return max(0, self.max_requests - len(current_requests))
