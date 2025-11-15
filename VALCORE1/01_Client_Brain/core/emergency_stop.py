"""
VALCORE1 Emergency Stop System
Panic hotkey (Ctrl+Shift+Alt+V) and kill switch
"""

import logging
import json
import psutil
import keyboard
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

PANIC_HOTKEY = 'ctrl+shift+alt+v'
STATE_DIR = Path("A:/000_START_HERE/VALCORE1_ROOT/Systems/VALCORE1/.state")


class EmergencyStop:
    """Emergency shutdown system with state preservation"""

    def __init__(self, voice_system=None, command_queue=None):
        """
        Initialize emergency stop system

        Args:
            voice_system: Reference to voice system for checking mic state
            command_queue: Reference to command queue for checking pending commands
        """
        self.enabled = True
        self.voice_system = voice_system
        self.command_queue = command_queue
        self.state_dir = Path(".state")  # Relative to current directory
        self.state_dir.mkdir(exist_ok=True)

        # Register hotkey
        try:
            keyboard.add_hotkey(PANIC_HOTKEY, self.trigger_shutdown)
            logger.info(f"Emergency stop hotkey registered: {PANIC_HOTKEY}")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")

    def get_active_room(self) -> str:
        """
        Get currently active room

        Returns:
            Room name
        """
        try:
            with open('config/room_contexts.json', 'r') as f:
                config = json.load(f)
            return config.get('active_room', 'general')
        except Exception as e:
            logger.error(f"Error getting active room: {e}")
            return 'general'

    def get_command_queue(self) -> List:
        """
        Get pending commands (if any)

        Returns:
            List of pending commands
        """
        if self.command_queue is None:
            return []

        try:
            # Try to get all items from queue without blocking
            commands = []
            while not self.command_queue.empty():
                try:
                    commands.append(self.command_queue.get_nowait())
                except:
                    break
            # Put them back
            for cmd in commands:
                self.command_queue.put(cmd)
            return commands
        except Exception as e:
            logger.error(f"Error accessing command queue: {e}")
            return []

    def get_mic_state(self) -> str:
        """
        Get microphone state

        Returns:
            "enabled" or "disabled"
        """
        if self.voice_system is None:
            return "unknown"

        try:
            # Check if voice system microphone is enabled
            if hasattr(self.voice_system, 'microphone_enabled'):
                return "enabled" if self.voice_system.microphone_enabled else "disabled"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"Error checking mic state: {e}")
            return "unknown"

    def save_checkpoint(self, reason: str = "emergency_stop"):
        """
        Save current state before shutdown

        Args:
            reason: Reason for checkpoint
        """
        try:
            checkpoint = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "active_room": self.get_active_room(),
                "pending_commands": self.get_command_queue(),
                "mic_state": self.get_mic_state()
            }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.state_dir / f"checkpoint_{timestamp}.json"

            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)

            logger.info(f"Checkpoint saved: {checkpoint_file}")

        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")

    def kill_all_valcore_processes(self) -> List[str]:
        """
        Terminate all VALCORE1 processes immediately

        Returns:
            List of killed process names
        """
        killed = []

        try:
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or []).lower()

                    # Check if process is related to VALCORE1
                    if any(keyword in cmdline for keyword in ['valcore', 'voice_system', 'main_client']):
                        proc_name = proc.info['name']
                        proc.kill()
                        killed.append(proc_name)
                        logger.info(f"Killed process: {proc_name}")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        except Exception as e:
            logger.error(f"Error killing processes: {e}")

        return killed

    def log_emergency_stop(self):
        """Log emergency stop event"""
        log_file = Path("logs/emergency.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} | EMERGENCY_STOP | User triggered panic hotkey\n")

        except Exception as e:
            logger.error(f"Error logging emergency stop: {e}")

    def trigger_shutdown(self):
        """Execute emergency shutdown"""
        print("\n" + "="*60)
        print("🚨 EMERGENCY STOP TRIGGERED 🚨")
        print("="*60 + "\n")

        # Save state
        print("Saving checkpoint...")
        self.save_checkpoint("panic_hotkey")

        # Kill processes
        print("Terminating VALCORE1 processes...")
        killed = self.kill_all_valcore_processes()
        print(f"✓ Killed {len(killed)} processes")

        # Log event
        self.log_emergency_stop()

        print(f"\n✓ Emergency stop complete")
        print(f"State saved to: {self.state_dir.absolute()}")
        print("\nTo resume: Run START_VALCORE1.bat\n")

        # Exit
        import sys
        sys.exit(0)

    def cleanup(self):
        """Cleanup emergency stop system"""
        try:
            keyboard.remove_hotkey(PANIC_HOTKEY)
        except:
            pass

        logger.info("Emergency stop system cleaned up")


def recover_from_checkpoint(checkpoint_file: Path) -> Dict:
    """
    Recover state from checkpoint file

    Args:
        checkpoint_file: Path to checkpoint JSON

    Returns:
        Checkpoint data dictionary
    """
    try:
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error recovering checkpoint: {e}")
        return {}


def find_latest_checkpoint() -> Path:
    """
    Find most recent checkpoint file

    Returns:
        Path to latest checkpoint or None
    """
    state_dir = Path(".state")

    if not state_dir.exists():
        return None

    checkpoints = list(state_dir.glob("checkpoint_*.json"))

    if not checkpoints:
        return None

    # Sort by modification time, most recent first
    checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return checkpoints[0]
