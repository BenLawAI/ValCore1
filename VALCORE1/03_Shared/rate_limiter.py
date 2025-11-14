"""
VALCORE1 Rate Limiter
Simple in-memory rate limiting for Flask API endpoints
"""

import logging
import time
from collections import defaultdict, deque
from functools import wraps
from typing import Callable, Optional, Tuple
from flask import request, jsonify

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self):
        """Initialize rate limiter"""
        # Store request timestamps per client
        # Format: {client_id: deque([timestamp1, timestamp2, ...])}
        self.clients = defaultdict(lambda: deque())

        # Store violation counts per client (for logging/blocking)
        self.violations = defaultdict(int)

        logger.info("Rate limiter initialized")

    def _get_client_id(self) -> str:
        """
        Get unique client identifier

        Returns:
            Client identifier (IP address + User-Agent hash)
        """
        # Use IP address as primary identifier
        ip = request.remote_addr or 'unknown'

        # Add user agent for better uniqueness
        user_agent = request.headers.get('User-Agent', 'unknown')
        user_agent_hash = str(hash(user_agent))[:8]

        return f"{ip}:{user_agent_hash}"

    def is_allowed(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
        client_id: Optional[str] = None
    ) -> Tuple[bool, dict]:
        """
        Check if request is allowed based on rate limit

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            client_id: Client identifier (auto-detected if None)

        Returns:
            (is_allowed, rate_limit_info)
        """
        if client_id is None:
            client_id = self._get_client_id()

        current_time = time.time()
        client_history = self.clients[client_id]

        # Remove requests outside the current window
        cutoff_time = current_time - window_seconds

        while client_history and client_history[0] < cutoff_time:
            client_history.popleft()

        # Count requests in current window
        request_count = len(client_history)

        # Check if limit exceeded
        if request_count >= max_requests:
            self.violations[client_id] += 1

            # Calculate retry-after time
            if client_history:
                oldest_request = client_history[0]
                retry_after = int(oldest_request + window_seconds - current_time)
            else:
                retry_after = window_seconds

            logger.warning(
                f"Rate limit exceeded for {client_id}: "
                f"{request_count}/{max_requests} in {window_seconds}s "
                f"(violations: {self.violations[client_id]})"
            )

            return False, {
                'allowed': False,
                'limit': max_requests,
                'remaining': 0,
                'reset_in': retry_after,
                'retry_after': retry_after
            }

        # Add current request
        client_history.append(current_time)

        return True, {
            'allowed': True,
            'limit': max_requests,
            'remaining': max_requests - request_count - 1,
            'reset_in': window_seconds
        }

    def reset_client(self, client_id: Optional[str] = None):
        """
        Reset rate limit for a client

        Args:
            client_id: Client identifier (current client if None)
        """
        if client_id is None:
            client_id = self._get_client_id()

        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Rate limit reset for {client_id}")

        if client_id in self.violations:
            del self.violations[client_id]

    def get_stats(self) -> dict:
        """
        Get rate limiter statistics

        Returns:
            Statistics dictionary
        """
        total_clients = len(self.clients)
        total_violations = sum(self.violations.values())

        # Get top violators
        top_violators = sorted(
            self.violations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'total_clients': total_clients,
            'total_violations': total_violations,
            'top_violators': [
                {'client_id': cid, 'violations': count}
                for cid, count in top_violators
            ]
        }

    def cleanup_old_entries(self, max_age_hours: int = 24):
        """
        Clean up old entries to prevent memory buildup

        Args:
            max_age_hours: Remove entries older than this
        """
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)

        cleaned_count = 0

        # Clean up client histories
        for client_id in list(self.clients.keys()):
            client_history = self.clients[client_id]

            # Remove old timestamps
            while client_history and client_history[0] < cutoff_time:
                client_history.popleft()

            # Remove client if no recent requests
            if not client_history:
                del self.clients[client_id]
                cleaned_count += 1

                # Also remove violations
                if client_id in self.violations:
                    del self.violations[client_id]

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old rate limit entries")


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(
    max_requests: int = 60,
    window_seconds: int = 60,
    per: str = "minute"
) -> Callable:
    """
    Decorator to apply rate limiting to Flask routes

    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def endpoint():
            return jsonify({"message": "Success"})

    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        per: Human-readable period (for display only)

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            allowed, info = _rate_limiter.is_allowed(max_requests, window_seconds)

            # Add rate limit headers
            response_headers = {
                'X-RateLimit-Limit': str(info['limit']),
                'X-RateLimit-Remaining': str(info['remaining']),
                'X-RateLimit-Reset': str(int(time.time() + info['reset_in']))
            }

            if not allowed:
                # Rate limit exceeded
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {max_requests} per {per}',
                    'retry_after': info['retry_after'],
                    'status': 'rate_limit_exceeded'
                })

                response.status_code = 429
                response.headers.update(response_headers)
                response.headers['Retry-After'] = str(info['retry_after'])

                return response

            # Request allowed, call the function
            result = f(*args, **kwargs)

            # Add rate limit headers to successful response
            if hasattr(result, 'headers'):
                result.headers.update(response_headers)

            return result

        return wrapped
    return decorator


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance

    Returns:
        RateLimiter instance
    """
    return _rate_limiter
