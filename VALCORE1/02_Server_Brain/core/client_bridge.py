"""
VALCORE1 Client Bridge
Flask server to receive and process client requests
"""

import logging
import json
import os
import sys
from pathlib import Path
from typing import Dict
from datetime import datetime

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_Shared"))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available")

from auth import APIAuth
from config_loader import ConfigLoader
from validators import validate_request, InputValidator
from rate_limiter import rate_limit, get_rate_limiter

logger = logging.getLogger(__name__)


class ClientBridge:
    """Flask server for client communication"""

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

        # Load environment configuration
        ConfigLoader.load_env_file()

        # Initialize authentication
        auth_enabled = ConfigLoader.get_bool('API_AUTH_ENABLED', default=False)
        auth_token = ConfigLoader.get_env('API_AUTH_TOKEN')
        self.auth = APIAuth(enabled=auth_enabled, token=auth_token)

        # Create Flask app
        self.app = Flask(__name__)

        # Configure CORS with environment variables
        allowed_origins = ConfigLoader.get_list('ALLOWED_CORS_ORIGINS', default=['*'])
        if allowed_origins == ['*']:
            logger.warning("CORS allows ALL origins - set ALLOWED_CORS_ORIGINS in .env for production!")
            CORS(self.app)
        else:
            logger.info(f"CORS restricted to: {allowed_origins}")
            CORS(self.app, origins=allowed_origins)

        # Register routes
        self._register_routes()

        # Server stats
        self.start_time = datetime.now()
        self.request_count = 0

        logger.info("Client bridge initialized")

    def _register_routes(self):
        """Register Flask routes"""

        @self.app.route('/api/health', methods=['GET'])
        @rate_limit(max_requests=120, window_seconds=60, per="minute")
        def health_check():
            """Health check endpoint"""
            uptime = (datetime.now() - self.start_time).total_seconds()

            return jsonify({
                "status": "ok",
                "model": self.llm.default_model,
                "uptime_seconds": uptime,
                "request_count": self.request_count
            })

        @self.app.route('/api/process', methods=['POST'])
        @rate_limit(max_requests=30, window_seconds=60, per="minute")
        @self.auth.require_auth
        @validate_request({
            'user_input': {'type': 'string', 'required': True, 'min_length': 1, 'max_length': 10000},
            'session_id': {'type': 'string', 'required': False, 'max_length': 64, 'pattern': InputValidator.PATTERNS['session_id']},
            'room': {'type': 'string', 'required': False, 'max_length': 32, 'pattern': InputValidator.PATTERNS['room_name']},
            'temperature': {'type': 'float', 'required': False, 'min_value': 0.0, 'max_value': 2.0},
            'max_tokens': {'type': 'integer', 'required': False, 'min_value': 1, 'max_value': 100000}
        })
        def process_request():
            """Process client request (requires authentication)"""
            try:
                self.request_count += 1

                # Use validated data
                data = request.validated_data

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
        @rate_limit(max_requests=60, window_seconds=60, per="minute")
        @self.auth.require_auth
        @validate_request({
            'query': {'type': 'string', 'required': True, 'min_length': 1, 'max_length': 1000},
            'room': {'type': 'string', 'required': False, 'max_length': 32, 'pattern': InputValidator.PATTERNS['room_name']},
            'max_results': {'type': 'integer', 'required': False, 'min_value': 1, 'max_value': 100}
        })
        def search_library():
            """Search library (requires authentication)"""
            try:
                # Use validated data
                data = request.validated_data

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
        @rate_limit(max_requests=20, window_seconds=60, per="minute")
        @self.auth.require_auth
        @validate_request({
            'session_id': {'type': 'string', 'required': False, 'max_length': 64, 'pattern': InputValidator.PATTERNS['session_id']},
            'room': {'type': 'string', 'required': True, 'max_length': 32, 'pattern': InputValidator.PATTERNS['room_name']}
        })
        def switch_room():
            """Switch room (requires authentication)"""
            try:
                # Use validated data
                data = request.validated_data

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
        @rate_limit(max_requests=100, window_seconds=60, per="minute")
        @self.auth.require_auth
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
