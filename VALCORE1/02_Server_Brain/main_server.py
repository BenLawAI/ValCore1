"""
VALCORE1 Server Brain - Main Entry Point
Runs on ATOM server (NVIDIA Blackwell GB10, 128GB unified memory)
"""

import sys
import logging
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.large_llm_interface import LargeLLM
from core.librarian import Librarian
from core.memory_compression import MemoryCompressor
from core.room_manager import RoomManager
from core.client_bridge import ClientBridge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/valcore1_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class VALCOREServer:
    """Main VALCORE1 server application"""

    def __init__(self, library_path: str = None):
        """Initialize VALCORE1 server"""
        logger.info("="*60)
        logger.info("VALCORE1 SERVER BRAIN STARTING")
        logger.info("="*60)

        # Determine library path
        if library_path is None:
            # Try to use absolute path, fall back to relative
            abs_path = Path("/home/user/ValCore1/Library")
            if abs_path.exists():
                library_path = str(abs_path)
            else:
                library_path = "../../Library"  # Relative path
                Path(library_path).mkdir(parents=True, exist_ok=True)

        logger.info(f"Library path: {library_path}")

        # Initialize components
        try:
            logger.info("Initializing components...")

            # LLM
            self.llm = LargeLLM('config/settings.json')

            # Librarian
            self.librarian = Librarian(library_path)

            # Room Manager
            room_config_path = '../01_Client_Brain/config/room_contexts.json'
            if not Path(room_config_path).exists():
                room_config_path = 'config/room_contexts.json'  # Fallback

            if Path(room_config_path).exists():
                self.room_manager = RoomManager(room_config_path, self.librarian)
            else:
                logger.warning("Room config not found, room management disabled")
                self.room_manager = None

            # Memory Compressor
            self.compressor = MemoryCompressor('config/compression_strategy.json', self.librarian)

            # Client Bridge
            self.bridge = ClientBridge(self.llm, self.librarian, self.room_manager)

            logger.info("All components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            sys.exit(1)

    def run(self):
        """Main server loop"""
        try:
            # Start compression scheduler
            logger.info("Starting compression scheduler...")
            self.compressor.start_scheduler()

            # Start server
            logger.info("Starting client bridge server...")
            logger.info("Server ready to accept client connections")
            logger.info("")

            # Run Flask server (blocking)
            self.bridge.start_server(host='0.0.0.0', port=5000)

        except KeyboardInterrupt:
            logger.info("\nShutting down gracefully...")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources before exit"""
        logger.info("Cleaning up...")

        if hasattr(self, 'compressor'):
            self.compressor.stop_scheduler()

        if hasattr(self, 'librarian'):
            self.librarian.save_index()

        logger.info("VALCORE1 Server stopped")


def main():
    """Entry point"""
    # Create logs directory
    Path("logs").mkdir(parents=True, exist_ok=True)

    # Parse command line arguments for library path (optional)
    library_path = None
    if len(sys.argv) > 1:
        library_path = sys.argv[1]

    # Run server
    server = VALCOREServer(library_path)
    server.run()


if __name__ == "__main__":
    main()
