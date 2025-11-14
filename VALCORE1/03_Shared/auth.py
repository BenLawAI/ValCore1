"""
VALCORE1 Authentication Module
Simple token-based authentication for Flask API
"""

import logging
import secrets
import hashlib
from functools import wraps
from typing import Optional, Callable
from flask import request, jsonify

logger = logging.getLogger(__name__)


class APIAuth:
    """Simple token-based API authentication"""

    def __init__(self, enabled: bool = True, token: Optional[str] = None):
        """
        Initialize API authentication

        Args:
            enabled: Enable authentication
            token: API token (auto-generated if None)
        """
        self.enabled = enabled

        if self.enabled:
            if token:
                # Hash the provided token for storage
                self.token_hash = self._hash_token(token)
                logger.info("API authentication enabled with provided token")
            else:
                # Generate a secure random token
                self.token = secrets.token_urlsafe(32)
                self.token_hash = self._hash_token(self.token)
                logger.warning("="*60)
                logger.warning("API TOKEN GENERATED (save this securely!):")
                logger.warning(f"  {self.token}")
                logger.warning("="*60)
                logger.warning("Set this in your .env file as API_AUTH_TOKEN")
                logger.warning("Clients must include header: Authorization: Bearer <token>")
        else:
            self.token_hash = None
            logger.warning("API authentication is DISABLED - API is publicly accessible!")

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        Hash token for secure storage

        Args:
            token: Plain token

        Returns:
            Hashed token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, token: str) -> bool:
        """
        Verify API token

        Args:
            token: Token to verify

        Returns:
            True if valid
        """
        if not self.enabled:
            return True

        if not token:
            return False

        token_hash = self._hash_token(token)
        return secrets.compare_digest(token_hash, self.token_hash)

    def require_auth(self, f: Callable) -> Callable:
        """
        Decorator to require authentication on Flask routes

        Usage:
            @app.route('/api/protected')
            @auth.require_auth
            def protected_endpoint():
                return jsonify({"message": "Access granted"})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip auth if disabled
            if not self.enabled:
                return f(*args, **kwargs)

            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                logger.warning(f"Unauthorized request to {request.path} - no Authorization header")
                return jsonify({
                    "error": "Missing Authorization header",
                    "status": "unauthorized"
                }), 401

            # Parse "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                logger.warning(f"Unauthorized request to {request.path} - invalid Authorization format")
                return jsonify({
                    "error": "Invalid Authorization header format. Use: Bearer <token>",
                    "status": "unauthorized"
                }), 401

            token = parts[1]

            # Verify token
            if not self.verify_token(token):
                logger.warning(f"Unauthorized request to {request.path} - invalid token")
                return jsonify({
                    "error": "Invalid API token",
                    "status": "unauthorized"
                }), 401

            # Token valid, proceed
            return f(*args, **kwargs)

        return decorated_function

    def optional_auth(self, f: Callable) -> Callable:
        """
        Decorator for optional authentication (still validates if provided)

        Usage:
            @app.route('/api/public-but-better-with-auth')
            @auth.optional_auth
            def endpoint():
                # Check request.authenticated = True/False
                return jsonify({"message": "Hello"})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Mark request as authenticated
            request.authenticated = False

            if not self.enabled:
                request.authenticated = True
                return f(*args, **kwargs)

            auth_header = request.headers.get('Authorization')

            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]
                    if self.verify_token(token):
                        request.authenticated = True

            return f(*args, **kwargs)

        return decorated_function


def generate_api_token() -> str:
    """
    Generate a secure API token

    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)
