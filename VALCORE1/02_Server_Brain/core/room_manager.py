"""
VALCORE1 Room Manager
Manages room contexts and switching
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class RoomManager:
    """Manages room contexts and history"""

    def __init__(self, config_path: str, librarian):
        """
        Initialize room manager

        Args:
            config_path: Path to room contexts config
            librarian: Librarian instance for context retrieval
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.librarian = librarian

        # Track active room per session
        self.session_rooms = {}  # session_id -> room_name

        logger.info(f"Room manager initialized with {len(self.config['rooms'])} rooms")

    def _load_config(self) -> dict:
        """Load room configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _save_config(self):
        """Save room configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_active_room(self, session_id: str) -> str:
        """
        Get active room for session

        Args:
            session_id: Session ID

        Returns:
            Room name
        """
        return self.session_rooms.get(session_id, self.config['active_room'])

    def switch_room(self, session_id: str, room_name: str) -> bool:
        """
        Switch to a different room

        Args:
            session_id: Session ID
            room_name: Target room name

        Returns:
            True if successful
        """
        if room_name not in self.config['rooms']:
            logger.error(f"Room '{room_name}' does not exist")
            return False

        self.session_rooms[session_id] = room_name
        logger.info(f"Session {session_id} switched to room: {room_name}")

        return True

    def get_room_config(self, room_name: str) -> Optional[Dict]:
        """
        Get configuration for a room

        Args:
            room_name: Room name

        Returns:
            Room configuration dict or None
        """
        return self.config['rooms'].get(room_name)

    def get_room_context(self, room_name: str, max_history: int = 10) -> str:
        """
        Get context for a room (recent conversation history)

        Args:
            room_name: Room name
            max_history: Maximum history entries

        Returns:
            Context string
        """
        # Get recent conversations from librarian
        recent = self.librarian.get_room_context(room_name, last_n=max_history)

        if not recent:
            return ""

        # Format as context
        context_lines = []
        for entry in reversed(recent):  # Chronological order
            text = entry.get('text', '')
            timestamp = entry.get('timestamp', '')
            context_lines.append(f"[{timestamp}] {text}")

        return "\n".join(context_lines)

    def list_rooms(self) -> List[str]:
        """
        Get list of all room names

        Returns:
            List of room names
        """
        return list(self.config['rooms'].keys())

    def create_room(self, name: str, config: Dict) -> bool:
        """
        Create a new room

        Args:
            name: Room name
            config: Room configuration

        Returns:
            True if successful
        """
        if name in self.config['rooms']:
            logger.error(f"Room '{name}' already exists")
            return False

        # Validate config has required fields
        required_fields = ['system_prompt', 'llm_temperature']
        if not all(field in config for field in required_fields):
            logger.error(f"Room config missing required fields: {required_fields}")
            return False

        # Add room
        self.config['rooms'][name] = config
        self._save_config()

        logger.info(f"Created new room: {name}")

        return True

    def delete_room(self, name: str) -> bool:
        """
        Delete a room

        Args:
            name: Room name

        Returns:
            True if successful
        """
        if name not in self.config['rooms']:
            logger.error(f"Room '{name}' does not exist")
            return False

        # Don't allow deleting the last room
        if len(self.config['rooms']) == 1:
            logger.error("Cannot delete the last room")
            return False

        # Remove room
        del self.config['rooms'][name]

        # Update active room if it was deleted
        if self.config['active_room'] == name:
            self.config['active_room'] = list(self.config['rooms'].keys())[0]

        # Remove from session tracking
        for session_id, room in list(self.session_rooms.items()):
            if room == name:
                self.session_rooms[session_id] = self.config['active_room']

        self._save_config()

        logger.info(f"Deleted room: {name}")

        return True

    def update_room_config(self, name: str, config: Dict) -> bool:
        """
        Update room configuration

        Args:
            name: Room name
            config: Updated configuration

        Returns:
            True if successful
        """
        if name not in self.config['rooms']:
            logger.error(f"Room '{name}' does not exist")
            return False

        # Update config
        self.config['rooms'][name].update(config)
        self._save_config()

        logger.info(f"Updated room config: {name}")

        return True

    def get_room_stats(self, room_name: str) -> Dict:
        """
        Get statistics for a room

        Args:
            room_name: Room name

        Returns:
            Statistics dictionary
        """
        # Count conversations in this room
        room_entries = [
            entry for entry in self.librarian.metadata
            if entry.get('room') == room_name
        ]

        return {
            "name": room_name,
            "conversation_count": len(room_entries),
            "config": self.get_room_config(room_name)
        }
