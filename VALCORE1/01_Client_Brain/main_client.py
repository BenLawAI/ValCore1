"""
VALCORE1 Client Brain - Main Entry Point
Runs on Ben's Desktop (RTX 5070 + RTX 4070)
"""

import sys
import logging
import json
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.voice_system_unified import VALVoiceSystem
from core.server_bridge import ServerBridge
from core.automation import Automation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/valcore1_client.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class VALCOREClient:
    """Main VALCORE1 client application"""

    def __init__(self):
        """Initialize VALCORE1 client"""
        logger.info("="*60)
        logger.info("VALCORE1 CLIENT BRAIN STARTING")
        logger.info("="*60)

        # Load room contexts
        with open('config/room_contexts.json', 'r') as f:
            self.room_config = json.load(f)
        self.active_room = self.room_config['active_room']

        # Initialize components
        try:
            logger.info("Initializing components...")

            self.voice = VALVoiceSystem('config/voice_config.json')
            self.server = ServerBridge('config/network_config.json')
            self.automation = Automation()

            logger.info("All components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            sys.exit(1)

    def handle_voice_command(self, text: str):
        """
        Handle transcribed voice command

        Args:
            text: Transcribed text from voice system
        """
        # Security: Don't log user input (may contain sensitive data)
        logger.info(f"[{self.active_room}] Processing user command ({len(text)} chars)")

        # Check for system commands
        text_lower = text.lower()

        # Microphone control
        if "mic off" in text_lower or "microphone off" in text_lower:
            self.voice.toggle_microphone()
            self.voice.synthesize_speech("Microphone disabled")
            return

        if "mic on" in text_lower or "microphone on" in text_lower:
            self.voice.toggle_microphone()
            self.voice.synthesize_speech("Microphone enabled")
            return

        # Room switching
        if "switch to" in text_lower:
            for room in self.room_config['rooms'].keys():
                if room in text_lower:
                    self.active_room = room
                    self.room_config['active_room'] = room
                    logger.info(f"Switched to room: {room}")
                    self.voice.synthesize_speech(f"Switched to {room} room")
                    return

        # Emergency stop
        if "emergency stop" in text_lower or "undo" in text_lower:
            logger.warning("Emergency undo triggered by voice")
            self.automation.emergency_undo()
            self.voice.synthesize_speech("Undoing last actions")
            return

        # Get current room configuration
        current_room = self.room_config['rooms'][self.active_room]
        system_prompt = current_room['system_prompt']

        # Query LLM (server or fallback)
        response = self.server.query_llm(
            prompt=text,
            context=system_prompt,
            room_config=current_room
        )

        if response:
            # Security: Don't log response (may contain sensitive data)
            logger.info(f"Generated response ({len(response)} chars)")

            # Speak response
            self.voice.synthesize_speech(response)

            # Auto-type if requested
            if "type this" in text_lower:
                logger.info("Auto-typing response to active window")
                self.automation.type_to_active_window(response)
        else:
            error_msg = "Sorry Boss, I'm having trouble processing that."
            logger.error(error_msg)
            self.voice.synthesize_speech(error_msg)

    def run(self):
        """Main application loop"""
        try:
            logger.info("Starting voice system...")
            logger.info(f"Active room: {self.active_room}")
            logger.info("Say 'Hey Val' to activate")
            logger.info("")

            # Start listening
            self.voice.start_listening(callback=self.handle_voice_command)

            # Keep running
            logger.info("VALCORE1 is running. Press Ctrl+C to stop.")
            while True:
                import time
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\nShutting down gracefully...")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources before exit"""
        logger.info("Cleaning up...")

        if hasattr(self, 'voice'):
            self.voice.cleanup()

        logger.info("VALCORE1 Client stopped")


def main():
    """Entry point"""
    # Create logs directory
    Path("logs/screenshots").mkdir(parents=True, exist_ok=True)

    # Run client
    client = VALCOREClient()
    client.run()


if __name__ == "__main__":
    main()
