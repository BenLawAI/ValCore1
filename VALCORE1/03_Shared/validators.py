"""
VALCORE1 Input Validation Module
Validate and sanitize API inputs to prevent injection attacks
"""

import re
import logging
from typing import Any, Dict, Optional, List
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validation utilities"""

    # Common validation patterns
    PATTERNS = {
        'session_id': re.compile(r'^[a-zA-Z0-9_-]{1,64}$'),
        'room_name': re.compile(r'^[a-zA-Z0-9_-]{1,32}$'),
        'model_name': re.compile(r'^[a-zA-Z0-9._:-]{1,64}$'),
    }

    # Maximum lengths for different input types
    MAX_LENGTHS = {
        'user_input': 10000,  # 10K characters for user prompts
        'query': 1000,        # 1K for search queries
        'text': 50000,        # 50K for bulk text
        'filename': 255,      # Standard filename length
        'path': 4096,         # Standard path length
    }

    @staticmethod
    def validate_string(
        value: Any,
        field_name: str,
        required: bool = True,
        min_length: int = 0,
        max_length: Optional[int] = None,
        pattern: Optional[re.Pattern] = None,
        allowed_chars: Optional[str] = None
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate string input

        Args:
            value: Value to validate
            field_name: Name of field (for error messages)
            required: Whether field is required
            min_length: Minimum length
            max_length: Maximum length
            pattern: Regex pattern to match
            allowed_chars: String of allowed characters

        Returns:
            (is_valid, sanitized_value, error_message)
        """
        # Check if provided
        if value is None or value == '':
            if required:
                return False, None, f"{field_name} is required"
            return True, '', None

        # Check type
        if not isinstance(value, str):
            return False, None, f"{field_name} must be a string"

        # Check length
        if len(value) < min_length:
            return False, None, f"{field_name} must be at least {min_length} characters"

        if max_length and len(value) > max_length:
            return False, None, f"{field_name} must be at most {max_length} characters"

        # Check pattern
        if pattern and not pattern.match(value):
            return False, None, f"{field_name} contains invalid characters or format"

        # Check allowed characters
        if allowed_chars:
            if not all(c in allowed_chars for c in value):
                return False, None, f"{field_name} contains disallowed characters"

        # Sanitize: strip leading/trailing whitespace
        sanitized = value.strip()

        return True, sanitized, None

    @staticmethod
    def validate_integer(
        value: Any,
        field_name: str,
        required: bool = True,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Validate integer input

        Args:
            value: Value to validate
            field_name: Name of field
            required: Whether field is required
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            (is_valid, converted_value, error_message)
        """
        # Check if provided
        if value is None:
            if required:
                return False, None, f"{field_name} is required"
            return True, None, None

        # Try to convert to int
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, None, f"{field_name} must be an integer"

        # Check range
        if min_value is not None and int_value < min_value:
            return False, None, f"{field_name} must be at least {min_value}"

        if max_value is not None and int_value > max_value:
            return False, None, f"{field_name} must be at most {max_value}"

        return True, int_value, None

    @staticmethod
    def validate_float(
        value: Any,
        field_name: str,
        required: bool = True,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> tuple[bool, Optional[float], Optional[str]]:
        """
        Validate float input

        Args:
            value: Value to validate
            field_name: Name of field
            required: Whether field is required
            min_value: Minimum value
            max_value: Maximum value

        Returns:
            (is_valid, converted_value, error_message)
        """
        # Check if provided
        if value is None:
            if required:
                return False, None, f"{field_name} is required"
            return True, None, None

        # Try to convert to float
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, None, f"{field_name} must be a number"

        # Check range
        if min_value is not None and float_value < min_value:
            return False, None, f"{field_name} must be at least {min_value}"

        if max_value is not None and float_value > max_value:
            return False, None, f"{field_name} must be at most {max_value}"

        return True, float_value, None

    @staticmethod
    def validate_boolean(
        value: Any,
        field_name: str,
        required: bool = True
    ) -> tuple[bool, Optional[bool], Optional[str]]:
        """
        Validate boolean input

        Args:
            value: Value to validate
            field_name: Name of field
            required: Whether field is required

        Returns:
            (is_valid, converted_value, error_message)
        """
        if value is None:
            if required:
                return False, None, f"{field_name} is required"
            return True, None, None

        # Handle different boolean representations
        if isinstance(value, bool):
            return True, value, None

        if isinstance(value, str):
            lower = value.lower()
            if lower in ('true', '1', 'yes', 'on'):
                return True, True, None
            if lower in ('false', '0', 'no', 'off'):
                return True, False, None

        if isinstance(value, int):
            return True, bool(value), None

        return False, None, f"{field_name} must be a boolean"

    @staticmethod
    def sanitize_sql(text: str) -> str:
        """
        Sanitize input for SQL (basic protection)

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        # Remove or escape SQL dangerous characters
        # Note: This is basic protection. Always use parameterized queries!
        dangerous = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']

        for char in dangerous:
            text = text.replace(char, '')

        return text

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize HTML/XSS dangerous characters

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text


def validate_request(schema: Dict[str, Dict]) -> Callable:
    """
    Decorator to validate Flask request data against a schema

    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_request({
            'user_input': {'type': 'string', 'required': True, 'max_length': 1000},
            'temperature': {'type': 'float', 'required': False, 'min_value': 0.0, 'max_value': 2.0}
        })
        def endpoint():
            data = request.validated_data  # Use validated data
            ...

    Args:
        schema: Validation schema

    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                data = request.get_json()
            except Exception:
                return jsonify({
                    "error": "Invalid JSON in request body",
                    "status": "error"
                }), 400

            if data is None:
                data = {}

            validated_data = {}
            errors = []

            # Validate each field in schema
            for field_name, field_schema in schema.items():
                value = data.get(field_name)
                field_type = field_schema.get('type', 'string')

                if field_type == 'string':
                    is_valid, sanitized, error = InputValidator.validate_string(
                        value,
                        field_name,
                        required=field_schema.get('required', False),
                        min_length=field_schema.get('min_length', 0),
                        max_length=field_schema.get('max_length'),
                        pattern=field_schema.get('pattern')
                    )
                elif field_type == 'integer':
                    is_valid, sanitized, error = InputValidator.validate_integer(
                        value,
                        field_name,
                        required=field_schema.get('required', False),
                        min_value=field_schema.get('min_value'),
                        max_value=field_schema.get('max_value')
                    )
                elif field_type == 'float':
                    is_valid, sanitized, error = InputValidator.validate_float(
                        value,
                        field_name,
                        required=field_schema.get('required', False),
                        min_value=field_schema.get('min_value'),
                        max_value=field_schema.get('max_value')
                    )
                elif field_type == 'boolean':
                    is_valid, sanitized, error = InputValidator.validate_boolean(
                        value,
                        field_name,
                        required=field_schema.get('required', False)
                    )
                else:
                    is_valid = False
                    error = f"Unknown validation type: {field_type}"
                    sanitized = None

                if not is_valid:
                    errors.append(error)
                else:
                    validated_data[field_name] = sanitized

            # Return errors if any
            if errors:
                logger.warning(f"Validation errors on {request.path}: {errors}")
                return jsonify({
                    "error": "Validation failed",
                    "details": errors,
                    "status": "error"
                }), 400

            # Attach validated data to request
            request.validated_data = validated_data

            return f(*args, **kwargs)

        return wrapped
    return decorator
