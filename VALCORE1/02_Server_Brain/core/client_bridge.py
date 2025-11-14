"""
VALCORE1 Client Bridge
Flask server to receive and process client requests
"""

import logging
import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from functools import wraps

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_Shared"))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available")

try:
    from flasgger import Swagger
    SWAGGER_AVAILABLE = True
except ImportError:
    SWAGGER_AVAILABLE = False
    logging.warning("Flasgger not available - API docs disabled")

from exceptions import (
    RoomNotFoundError,
    RoomException,
    LLMException,
    StorageException,
    ValidationException,
    InputValidationError,
    RateLimitError
)

from security_utils import (
    RateLimiter,
    sanitize_json_input,
    validate_session_id,
    validate_room_name,
    validate_api_key
)

logger = logging.getLogger(__name__)


class ClientBridge:
    """Flask server for client communication"""

    def __init__(self, llm, librarian, room_manager=None, api_key: Optional[str] = None):
        """
        Initialize client bridge

        Args:
            llm: LargeLLM instance
            librarian: Librarian instance
            room_manager: RoomManager instance (optional)
            api_key: Optional API key for authentication
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for ClientBridge")

        self.llm = llm
        self.librarian = librarian
        self.room_manager = room_manager
        self.api_key = api_key or os.getenv('VALCORE1_API_KEY')

        # Create Flask app
        self.app = Flask(__name__)

        # CORS with restricted origins in production
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        CORS(self.app, origins=allowed_origins)

        # Initialize rate limiter (60 requests per minute by default)
        self.rate_limiter = RateLimiter(
            max_requests=int(os.getenv('RATE_LIMIT_REQUESTS', 60)),
            window_seconds=int(os.getenv('RATE_LIMIT_WINDOW', 60))
        )

        # Initialize Swagger if available
        if SWAGGER_AVAILABLE:
            self.swagger = Swagger(self.app, config={
                "headers": [],
                "specs": [
                    {
                        "endpoint": 'apispec',
                        "route": '/apispec.json',
                        "rule_filter": lambda rule: True,
                        "model_filter": lambda tag: True,
                    }
                ],
                "static_url_path": "/flasgger_static",
                "swagger_ui": True,
                "specs_route": "/api/docs"
            })
            logger.info("Swagger API documentation enabled at /api/docs")

        # Register routes
        self._register_routes()

        # Server stats
        self.start_time = datetime.now()
        self.request_count = 0

        logger.info("Client bridge initialized")

    def _check_rate_limit(self):
        """Check rate limit for current request"""
        # Use IP address as identifier
        identifier = request.remote_addr or 'unknown'

        if not self.rate_limiter.is_allowed(identifier):
            raise RateLimitError("Rate limit exceeded. Please try again later.")

        return identifier

    def _check_api_key(self):
        """Check API key if configured"""
        if self.api_key:
            provided_key = request.headers.get('X-API-Key')
            if not provided_key or not validate_api_key(provided_key, self.api_key):
                raise ValidationException("Invalid or missing API key")

    def _register_routes(self):
        """Register Flask routes"""

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """
            Health check endpoint
            ---
            tags:
              - health
            responses:
              200:
                description: Server health status
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      example: ok
                    model:
                      type: string
                      example: qwen2.5:14b
                    uptime_seconds:
                      type: number
                      example: 3600
                    request_count:
                      type: integer
                      example: 150
            """
            uptime = (datetime.now() - self.start_time).total_seconds()

            return jsonify({
                "status": "ok",
                "model": self.llm.default_model,
                "uptime_seconds": uptime,
                "request_count": self.request_count
            })

        @self.app.route('/api/process', methods=['POST'])
        def process_request():
            """
            Process client request and generate response
            ---
            tags:
              - inference
            parameters:
              - in: header
                name: X-API-Key
                type: string
                required: false
                description: API key for authentication (if enabled)
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - user_input
                  properties:
                    session_id:
                      type: string
                      example: user_123
                    user_input:
                      type: string
                      example: What's the weather today?
                    room:
                      type: string
                      example: general
            responses:
              200:
                description: Successful response
                schema:
                  type: object
                  properties:
                    response:
                      type: string
                    room:
                      type: string
                    timestamp:
                      type: string
                    latency_ms:
                      type: number
              400:
                description: Validation error
              429:
                description: Rate limit exceeded
              503:
                description: LLM service unavailable
            """
            try:
                # Check rate limit
                self._check_rate_limit()

                # Check API key if configured
                self._check_api_key()

                self.request_count += 1

                data = request.get_json()
                if not data:
                    raise InputValidationError("No JSON data provided")

                # Sanitize input
                data = sanitize_json_input(data)

                session_id = data.get('session_id', 'default')
                user_input = data.get('user_input', '')
                room = data.get('room', 'general')

                # Validate inputs
                if not user_input:
                    raise InputValidationError("user_input is required")

                if not validate_session_id(session_id):
                    raise InputValidationError("Invalid session_id format")

                if not validate_room_name(room):
                    raise InputValidationError("Invalid room name format")

                logger.info(f"Processing request from session {session_id} (room: {room})")

                # Get room configuration
                if self.room_manager:
                    room_config = self.room_manager.get_room_config(room)
                    system_prompt = room_config.get('system_prompt', '')
                    temperature = room_config.get('llm_temperature', 0.7)
                    max_tokens = room_config.get('max_tokens', 2000)

                    # Get room context
                    context = self.room_manager.get_room_context(room, max_history=5)
                else:
                    system_prompt = ""
                    temperature = 0.7
                    max_tokens = 2000
                    context = ""

                # Build full prompt
                full_prompt = user_input
                if context:
                    full_prompt = f"Previous context:\n{context}\n\nCurrent query: {user_input}"

                # Generate response
                start_time = datetime.now()

                response = self.llm.generate(
                    prompt=full_prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                latency = (datetime.now() - start_time).total_seconds() * 1000  # ms

                # Store in librarian
                self.librarian.add_conversation(
                    room=room,
                    text=user_input,
                    metadata={
                        "response": response,
                        "session_id": session_id,
                        "latency_ms": latency
                    }
                )

                return jsonify({
                    "response": response,
                    "room": room,
                    "timestamp": datetime.now().isoformat(),
                    "latency_ms": latency
                })

            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded: {request.remote_addr}")
                return jsonify({
                    "error": str(e),
                    "status": "rate_limit_exceeded"
                }), 429
            except InputValidationError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({
                    "error": str(e),
                    "status": "validation_error"
                }), 400
            except ValidationException as e:
                logger.warning(f"Authentication error: {e}")
                return jsonify({
                    "error": str(e),
                    "status": "authentication_error"
                }), 401
            except LLMException as e:
                logger.error(f"LLM error: {e}", exc_info=True)
                return jsonify({
                    "error": "LLM processing failed",
                    "details": str(e),
                    "status": "error"
                }), 503
            except StorageException as e:
                logger.error(f"Storage error: {e}", exc_info=True)
                return jsonify({
                    "error": "Storage operation failed",
                    "details": str(e),
                    "status": "error"
                }), 500
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error",
                    "status": "error"
                }), 500

        @self.app.route('/api/search', methods=['POST'])
        def search_library():
            """
            Search conversation library
            ---
            tags:
              - search
            parameters:
              - in: body
                name: body
                required: true
                schema:
                  type: object
                  required:
                    - query
                  properties:
                    query:
                      type: string
                      example: previous conversations about weather
                    room:
                      type: string
                      example: general
                    max_results:
                      type: integer
                      example: 10
            responses:
              200:
                description: Search results
                schema:
                  type: object
                  properties:
                    results:
                      type: array
                    count:
                      type: integer
            """
            try:
                # Check rate limit
                self._check_rate_limit()

                # Check API key if configured
                self._check_api_key()

                data = request.get_json()
                if not data:
                    raise InputValidationError("No JSON data provided")

                # Sanitize input
                data = sanitize_json_input(data)

                query = data.get('query', '')
                if not query:
                    raise InputValidationError("query parameter is required")

                room = data.get('room')  # None = search all rooms
                max_results = min(data.get('max_results', 10), 100)  # Cap at 100

                if room and not validate_room_name(room):
                    raise InputValidationError("Invalid room name format")

                logger.info(f"Searching library: {query}")

                results = self.librarian.search(
                    query=query,
                    room=room,
                    max_results=max_results
                )

                return jsonify({
                    "results": results,
                    "count": len(results)
                })

            except InputValidationError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({
                    "error": str(e),
                    "status": "validation_error"
                }), 400
            except StorageException as e:
                logger.error(f"Storage error: {e}", exc_info=True)
                return jsonify({
                    "error": "Search operation failed",
                    "details": str(e),
                    "status": "error"
                }), 500
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error",
                    "status": "error"
                }), 500

        @self.app.route('/api/room/switch', methods=['POST'])
        def switch_room():
            """Switch room"""
            try:
                data = request.get_json()
                if not data:
                    raise InputValidationError("No JSON data provided")

                session_id = data.get('session_id', 'default')
                room_name = data.get('room')

                if not room_name:
                    raise InputValidationError("room parameter required")

                if not self.room_manager:
                    raise RoomException("room_manager not configured")

                success = self.room_manager.switch_room(session_id, room_name)

                if success:
                    return jsonify({
                        "status": "ok",
                        "room": room_name
                    })
                else:
                    raise RoomNotFoundError(f"Room '{room_name}' not found")

            except InputValidationError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({
                    "error": str(e),
                    "status": "validation_error"
                }), 400
            except RoomNotFoundError as e:
                logger.warning(f"Room not found: {e}")
                return jsonify({
                    "error": str(e),
                    "status": "not_found"
                }), 404
            except RoomException as e:
                logger.error(f"Room error: {e}", exc_info=True)
                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error",
                    "status": "error"
                }), 500

        @self.app.route('/api/rooms', methods=['GET'])
        def list_rooms():
            """List available rooms"""
            try:
                if not self.room_manager:
                    return jsonify({
                        "error": "room_manager not configured",
                        "status": "error"
                    }), 500

                rooms = self.room_manager.list_rooms()

                return jsonify({
                    "rooms": rooms,
                    "count": len(rooms)
                })

            except RoomException as e:
                logger.error(f"Room error: {e}", exc_info=True)
                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return jsonify({
                    "error": "Internal server error",
                    "status": "error"
                }), 500

    def start_server(self, host: str = '0.0.0.0', port: int = 5000,
                     use_https: bool = False, cert_path: str = None, key_path: str = None):
        """
        Start Flask server with optional HTTPS support

        Args:
            host: Host to bind to
            port: Port to bind to
            use_https: Enable HTTPS/TLS
            cert_path: Path to SSL certificate file
            key_path: Path to SSL private key file
        """
        # Check for HTTPS configuration from environment
        if os.getenv('VALCORE1_HTTPS', 'false').lower() == 'true':
            use_https = True

        ssl_context = None
        if use_https:
            from security_utils import generate_self_signed_cert

            # Use provided certs or generate/use self-signed
            if cert_path and key_path:
                ssl_context = (cert_path, key_path)
                logger.info(f"Using provided SSL certificates: {cert_path}, {key_path}")
            else:
                cert_file, key_file = generate_self_signed_cert()
                ssl_context = (cert_file, key_file)

            protocol = "https"
        else:
            protocol = "http"
            logger.warning("Running server without HTTPS - use HTTPS in production!")

        logger.info(f"Starting server on {protocol}://{host}:{port}")
        if SWAGGER_AVAILABLE:
            logger.info(f"API documentation available at {protocol}://{host}:{port}/api/docs")

        self.app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            ssl_context=ssl_context
        )
