"""
VALCORE1 Network Fallback Manager
Handles offline mode, queue management, and conflict resolution
"""

import logging
import json
import queue
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import requests

logger = logging.getLogger(__name__)


class NetworkFallbackManager:
    """Manages offline operation and synchronization"""

    def __init__(self, config_path: str = "config/network_config.json"):
        """Initialize network fallback manager"""
        self.config = self._load_config(config_path)
        self.server_available = False
        self.offline_queue = queue.Queue()
        self.sync_in_progress = False
        self.conflict_log = []

        # Conflict log file
        self.conflict_log_file = Path("logs/conflict_log.json")
        self.conflict_log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Network fallback manager initialized")

    def _load_config(self, path: str) -> dict:
        """Load configuration"""
        with open(path, 'r') as f:
            return json.load(f)

    def get_server_url(self) -> str:
        """
        Get server URL (prefer Tailscale if configured)

        Returns:
            Server URL
        """
        if self.config.get('prefer_tailscale') and self.config.get('atom_tailscale_ip'):
            host = self.config['atom_tailscale_ip']
        else:
            host = self.config['atom_local_ip']

        port = self.config['atom_port']
        return f"http://{host}:{port}"

    def check_server_health(self) -> bool:
        """
        Ping ATOM server to check availability

        Returns:
            True if server is reachable
        """
        try:
            server_url = self.get_server_url()
            response = requests.get(
                f"{server_url}/api/health",
                timeout=5
            )
            self.server_available = (response.status_code == 200)

        except requests.exceptions.RequestException:
            self.server_available = False

        return self.server_available

    def send_to_server(self, message: Dict) -> Optional[Dict]:
        """
        Send message to server with automatic fallback

        Args:
            message: Message dictionary

        Returns:
            Server response if successful, None if offline
        """
        if not self.check_server_health():
            # Server unavailable, queue for later
            self.offline_queue.put(message)
            self.notify_user_offline_mode()
            return None

        try:
            server_url = self.get_server_url()
            response = requests.post(
                f"{server_url}/api/process",
                json=message,
                timeout=self.config['connection_timeout']
            )

            if response.status_code == 200:
                return response.json()

        except requests.exceptions.RequestException as e:
            # Connection failed mid-request
            logger.warning(f"Server request failed: {e}")
            self.offline_queue.put(message)
            self.server_available = False

        return None

    def sync_offline_queue(self):
        """Sync queued messages when server comes back online"""
        if self.sync_in_progress or self.offline_queue.empty():
            return

        if not self.check_server_health():
            return

        self.sync_in_progress = True
        self.notify_user_sync_started()

        synced = 0
        conflicts = 0

        while not self.offline_queue.empty():
            try:
                message = self.offline_queue.get_nowait()

                # Check for conflicts
                if self._has_conflict(message):
                    conflicts += 1
                    self.conflict_log.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": message,
                        "reason": "local_state_diverged_from_server"
                    })
                    continue

                # Send to server
                response = self.send_to_server(message)
                if response:
                    synced += 1
                else:
                    # Connection dropped again, re-queue
                    self.offline_queue.put(message)
                    break

            except queue.Empty:
                break

        # Save conflict log
        if conflicts > 0:
            self._save_conflict_log()

        self.sync_in_progress = False
        self.notify_user_sync_complete(synced, conflicts)

    def _has_conflict(self, message: Dict) -> bool:
        """
        Detect if local state conflicts with server state

        Args:
            message: Message to check

        Returns:
            True if conflict detected
        """
        message_type = message.get('type')

        if message_type == 'conversation':
            # Check if conversation exists on server with different content
            conversation_id = message.get('conversation_id')
            server_version = self._get_server_conversation_version(conversation_id)
            local_version = message.get('version')

            return server_version and server_version != local_version

        elif message_type == 'file_edit':
            # Check if file was modified on server
            file_path = message.get('file_path')
            server_timestamp = self._get_server_file_timestamp(file_path)
            local_timestamp = message.get('timestamp')

            if server_timestamp and local_timestamp:
                return server_timestamp > local_timestamp

        return False

    def _get_server_conversation_version(self, conversation_id: str) -> Optional[str]:
        """
        Get conversation version from server

        Args:
            conversation_id: Conversation ID

        Returns:
            Version (timestamp string) or None
        """
        try:
            server_url = self.get_server_url()
            response = requests.post(
                f"{server_url}/api/conversation/version",
                json={"conversation_id": conversation_id},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('version')

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get conversation version: {e}")

        return None

    def _get_server_file_timestamp(self, file_path: str) -> Optional[str]:
        """
        Get file timestamp from server

        Args:
            file_path: File path

        Returns:
            ISO timestamp or None
        """
        try:
            server_url = self.get_server_url()
            response = requests.post(
                f"{server_url}/api/file/timestamp",
                json={"file_path": file_path},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('timestamp')

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get file timestamp: {e}")

        return None

    def _fetch_from_server(self, message: Dict) -> Optional[Dict]:
        """
        Fetch latest version from server

        Args:
            message: Message with reference info

        Returns:
            Server conversation data or None
        """
        try:
            # Extract conversation ID from message
            conversation_id = message.get('conversation_id')
            if not conversation_id:
                logger.warning("No conversation_id in message")
                return None

            server_url = self.get_server_url()
            response = requests.post(
                f"{server_url}/api/conversation/fetch",
                json={"conversation_id": conversation_id},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('exists'):
                    logger.info(f"Fetched conversation {conversation_id} from server")
                    return data.get('conversation')
                else:
                    logger.warning(f"Conversation {conversation_id} not found on server")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch from server: {e}")

        return None

    def _merge_changes(self, message: Dict) -> bool:
        """
        Attempt automatic merge of changes

        Args:
            message: Message with changes

        Returns:
            True if merge successful, False otherwise
        """
        try:
            # Fetch server version
            server_data = self._fetch_from_server(message)
            if not server_data:
                logger.warning("Cannot merge: server data not available")
                return False

            # Simple merge strategy: combine text fields
            message_type = message.get('type')

            if message_type == 'conversation':
                # For conversations, append local changes to server version
                local_text = message.get('text', '')
                server_text = server_data.get('text', '')

                # Create merged version
                merged_message = {
                    **message,
                    'text': f"{server_text}\n\n[Local addition:]\n{local_text}",
                    'merged': True,
                    'merge_timestamp': datetime.now().isoformat()
                }

                # Send merged version to server
                response = self.send_to_server(merged_message)
                if response:
                    logger.info("Merge successful")
                    return True

            elif message_type == 'file_edit':
                # For file edits, we can't automatically merge
                # Log conflict for manual resolution
                logger.warning("Cannot auto-merge file edits - manual resolution required")
                return False

        except Exception as e:
            logger.error(f"Merge error: {e}")

        return False

    def resolve_conflict(self, conflict: Dict, resolution: str = "keep_local"):
        """
        Resolve conflict manually

        Args:
            conflict: Conflict from conflict_log
            resolution: "keep_local", "keep_server", or "merge"
        """
        if resolution == "keep_local":
            # Force send local version to server
            self.send_to_server(conflict['message'])
            logger.info("Conflict resolved: keeping local version")

        elif resolution == "keep_server":
            # Discard local changes, fetch server version
            self._fetch_from_server(conflict['message'])
            logger.info("Conflict resolved: keeping server version")

        elif resolution == "merge":
            # Attempt automatic merge
            self._merge_changes(conflict['message'])
            logger.info("Conflict resolved: attempting merge")

    def _save_conflict_log(self):
        """Save conflict log to disk"""
        try:
            with open(self.conflict_log_file, 'w') as f:
                json.dump(self.conflict_log, f, indent=2)

            logger.info(f"Conflict log saved: {len(self.conflict_log)} conflicts")

        except Exception as e:
            logger.error(f"Error saving conflict log: {e}")

    def notify_user_offline_mode(self):
        """Notify user that system is running in local mode"""
        logger.warning("⚠️  OFFLINE MODE - Server unavailable. Using local LLM.")
        logger.info("Messages will sync when connection is restored.")

    def notify_user_sync_started(self):
        """Notify user that sync is starting"""
        queue_size = self.offline_queue.qsize()
        logger.info(f"🔄 SYNC STARTED - Syncing {queue_size} queued messages...")

    def notify_user_sync_complete(self, synced: int, conflicts: int):
        """
        Notify user that sync completed

        Args:
            synced: Number of messages synced
            conflicts: Number of conflicts detected
        """
        logger.info(f"✓ SYNC COMPLETE - Synced: {synced} messages")

        if conflicts > 0:
            logger.warning(f"Conflicts: {conflicts} (review in conflict_log.json)")

    def get_status(self) -> Dict:
        """
        Get fallback manager status

        Returns:
            Status dictionary
        """
        return {
            "server_available": self.server_available,
            "queue_size": self.offline_queue.qsize(),
            "sync_in_progress": self.sync_in_progress,
            "conflicts": len(self.conflict_log)
        }
