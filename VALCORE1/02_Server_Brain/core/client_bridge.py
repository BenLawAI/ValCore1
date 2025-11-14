"""
VALCORE1 Client Bridge
Flask server to receive and process client requests
"""

import logging
import json
import os
from typing import Dict
from datetime import datetime
from functools import wraps

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available")

logger = logging.getLogger(__name__)


class ClientBridge:
    """Flask server for client communication with API key authentication"""

    def __init__(self, llm, librarian, room_manager=None):
        """
        Initialize client bridge

        Args:
            llm: LargeLLM instance
            librarian: Librarian instance
            room_manager: RoomManager instance (optional)
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for ClientBridge")

        self.llm = llm
        self.librarian = librarian
        self.room_manager = room_manager

        # Load API key from environment
        self._load_api_key()

        # Create Flask app
        self.app = Flask(__name__)

        # Configure CORS with restricted origins (security)
        self._configure_cors()

        # Register routes
        self._register_routes()

        # Server stats
        self.start_time = datetime.now()
        self.request_count = 0

        logger.info("Client bridge initialized with authentication")

    def _load_api_key(self):
        """
        Load API key from environment variable

        If no API key is set, authentication is disabled with a warning.
        """
        # Try to load .env file
        try:
            from dotenv import load_dotenv
            from pathlib import Path
            env_path = Path(__file__).parent.parent.parent.parent / '.env'
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
        except (ImportError, Exception):
            pass

        self.api_key = os.getenv('VALCORE_API_KEY')

        if not self.api_key:
            logger.warning("="*60)
            logger.warning("SECURITY WARNING: No API key configured!")
            logger.warning("Set VALCORE_API_KEY in .env file for production.")
            logger.warning("API endpoints are currently UNPROTECTED!")
            logger.warning("="*60)
            self.auth_enabled = False
        else:
            logger.info("API authentication enabled")
            self.auth_enabled = True

    def _configure_cors(self):
        """
        Configure CORS with restricted origins for security

        CORS is configured to only allow requests from:
        - Local network (192.168.*)
        - Localhost (127.0.0.1, localhost)
        - Tailscale network (100.64.* to 100.127.*)
        - Additional origins from CORS_ALLOWED_ORIGINS env variable

        This prevents unauthorized cross-origin requests while allowing
        legitimate clients to connect.
        """
        import re

        # Default allowed origins (regex patterns)
        allowed_origin_patterns = [
            r'^https?://localhost(:[0-9]+)?$',           # localhost
            r'^https?://127\.0\.0\.1(:[0-9]+)?$',        # 127.0.0.1
            r'^https?://192\.168\.[0-9]+\.[0-9]+(:[0-9]+)?$',  # Local network 192.168.*
            r'^https?://10\.[0-9]+\.[0-9]+\.[0-9]+(:[0-9]+)?$', # Local network 10.*
            r'^https?://172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]+\.[0-9]+(:[0-9]+)?$', # Local 172.16-31.*
            r'^https?://100\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7])\.[0-9]+\.[0-9]+(:[0-9]+)?$', # Tailscale 100.64-127.*
        ]

        # Load additional allowed origins from environment
        custom_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
        if custom_origins:
            # Split by comma and add to patterns
            for origin in custom_origins.split(','):
                origin = origin.strip()
                if origin:
                    # Escape special regex characters except * which we'll replace
                    escaped = re.escape(origin).replace(r'\*', '.*')
                    allowed_origin_patterns.append(f'^{escaped}$')
                    logger.info(f"Added custom CORS origin pattern: {origin}")

        # Compile patterns
        self.cors_patterns = [re.compile(pattern) for pattern in allowed_origin_patterns]

        # Configure CORS with origin validation
        CORS(
            self.app,
            resources={
                r"/api/*": {
                    "origins": self._validate_cors_origin,
                    "methods": ["GET", "POST", "OPTIONS"],
                    "allow_headers": ["Content-Type", "X-API-Key"],
                    "expose_headers": ["Content-Type"],
                    "supports_credentials": False,
                    "max_age": 3600  # Cache preflight for 1 hour
                }
            }
        )

        logger.info(f"CORS configured with {len(self.cors_patterns)} allowed origin patterns")
        logger.info("Allowed networks: localhost, 192.168.*, 10.*, 172.16-31.*, Tailscale")

    def _validate_cors_origin(self, origin):
        """
        Validate if origin is allowed based on patterns

        Args:
            origin: Origin header from request

        Returns:
            True if origin is allowed, False otherwise
        """
        if not origin:
            return False

        # Check against all patterns
        for pattern in self.cors_patterns:
            if pattern.match(origin):
                logger.debug(f"CORS: Allowed origin {origin}")
                return True

        # Log rejected origins for security monitoring
        logger.warning(f"CORS: Rejected origin {origin} from {request.remote_addr}")
        return False

    def _verify_api_key(self) -> bool:
        """
        Verify API key from request headers

        Returns:
            True if API key is valid or auth is disabled, False otherwise
        """
        # If auth is disabled, allow all requests (with warning logged at init)
        if not self.auth_enabled:
            return True

        # Check for API key in headers
        auth_header = request.headers.get('X-API-Key')

        if not auth_header:
            logger.warning(f"Missing API key from {request.remote_addr}")
            return False

        if auth_header != self.api_key:
            logger.warning(f"Invalid API key from {request.remote_addr}")
            return False

        return True

    def require_auth(self, f):
        """
        Decorator to require authentication for endpoints

        Usage:
            @self.require_auth
            def protected_endpoint():
                ...
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self._verify_api_key():
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Valid API key required. Set X-API-Key header."
                }), 401
            return f(*args, **kwargs)
        return decorated_function

    def _register_routes(self):
        """Register Flask routes"""

        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint (public - no authentication required)"""
            uptime = (datetime.now() - self.start_time).total_seconds()

            return jsonify({
                "status": "ok",
                "model": self.llm.default_model,
                "uptime_seconds": uptime,
                "request_count": self.request_count,
                "auth_enabled": self.auth_enabled
            })

        @self.app.route('/api/process', methods=['POST'])
        @self.require_auth
        def process_request():
            """Process client request"""
            try:
                self.request_count += 1

                data = request.get_json()

                session_id = data.get('session_id', 'default')
                user_input = data.get('user_input', '')
                room = data.get('room', 'general')

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

            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

        @self.app.route('/api/search', methods=['POST'])
        @self.require_auth
        def search_library():
            """Search library (requires authentication)"""
            try:
                data = request.get_json()

                query = data.get('query', '')
                room = data.get('room')  # None = search all rooms
                max_results = data.get('max_results', 10)

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

            except Exception as e:
                logger.error(f"Search error: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

        @self.app.route('/api/room/switch', methods=['POST'])
        @self.require_auth
        def switch_room():
            """Switch room (requires authentication)"""
            try:
                data = request.get_json()

                session_id = data.get('session_id', 'default')
                room_name = data.get('room')

                if not room_name:
                    return jsonify({
                        "error": "room parameter required",
                        "status": "error"
                    }), 400

                if not self.room_manager:
                    return jsonify({
                        "error": "room_manager not configured",
                        "status": "error"
                    }), 500

                success = self.room_manager.switch_room(session_id, room_name)

                if success:
                    return jsonify({
                        "status": "ok",
                        "room": room_name
                    })
                else:
                    return jsonify({
                        "error": f"Room '{room_name}' not found",
                        "status": "error"
                    }), 404

            except Exception as e:
                logger.error(f"Room switch error: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

        @self.app.route('/api/rooms', methods=['GET'])
        @self.require_auth
        def list_rooms():
            """List available rooms (requires authentication)"""
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

            except Exception as e:
                logger.error(f"List rooms error: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

    def start_server(self, host: str = '0.0.0.0', port: int = 5000):
        """
        Start Flask server

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting server on {host}:{port}")

        self.app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
