"""
VALCORE1 Client Bridge
Flask server to receive and process client requests
"""

import logging
import json
from typing import Dict
from datetime import datetime

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available")

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

        # Create Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes

        # Register routes
        self._register_routes()

        # Server stats
        self.start_time = datetime.now()
        self.request_count = 0

        logger.info("Client bridge initialized")

    def _register_routes(self):
        """Register Flask routes"""

        @self.app.route('/api/health', methods=['GET'])
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
        def search_library():
            """Search library"""
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
        def switch_room():
            """Switch room"""
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

            except Exception as e:
                logger.error(f"List rooms error: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

        @self.app.route('/api/conversation/version', methods=['POST'])
        def get_conversation_version():
            """Get conversation version for conflict detection"""
            try:
                data = request.get_json()
                conversation_id = data.get('conversation_id')

                if not conversation_id:
                    return jsonify({
                        "error": "conversation_id required",
                        "status": "error"
                    }), 400

                # Search librarian for conversation metadata
                results = self.librarian.search(
                    query=conversation_id,
                    max_results=1
                )

                if results:
                    version = results[0].get('metadata', {}).get('version', 1)
                    timestamp = results[0].get('metadata', {}).get('timestamp')

                    return jsonify({
                        "conversation_id": conversation_id,
                        "version": version,
                        "timestamp": timestamp,
                        "status": "ok"
                    })
                else:
                    return jsonify({
                        "conversation_id": conversation_id,
                        "exists": False,
                        "status": "ok"
                    })

            except Exception as e:
                logger.error(f"Get conversation version error: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

        @self.app.route('/api/file/timestamp', methods=['POST'])
        def get_file_timestamp():
            """Get file timestamp for conflict detection"""
            try:
                data = request.get_json()
                file_path = data.get('file_path')

                if not file_path:
                    return jsonify({
                        "error": "file_path required",
                        "status": "error"
                    }), 400

                # Check if file exists in librarian metadata
                results = self.librarian.search(
                    query=f"file:{file_path}",
                    max_results=1
                )

                if results:
                    timestamp = results[0].get('metadata', {}).get('timestamp')
                    return jsonify({
                        "file_path": file_path,
                        "timestamp": timestamp,
                        "exists": True,
                        "status": "ok"
                    })
                else:
                    return jsonify({
                        "file_path": file_path,
                        "exists": False,
                        "status": "ok"
                    })

            except Exception as e:
                logger.error(f"Get file timestamp error: {e}", exc_info=True)

                return jsonify({
                    "error": str(e),
                    "status": "error"
                }), 500

        @self.app.route('/api/conversation/fetch', methods=['POST'])
        def fetch_conversation():
            """Fetch conversation data from server"""
            try:
                data = request.get_json()
                conversation_id = data.get('conversation_id')
                room = data.get('room')

                if not conversation_id:
                    return jsonify({
                        "error": "conversation_id required",
                        "status": "error"
                    }), 400

                # Search librarian for conversation
                results = self.librarian.search(
                    query=conversation_id,
                    room=room,
                    max_results=10
                )

                return jsonify({
                    "conversation_id": conversation_id,
                    "results": results,
                    "count": len(results),
                    "status": "ok"
                })

            except Exception as e:
                logger.error(f"Fetch conversation error: {e}", exc_info=True)

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
