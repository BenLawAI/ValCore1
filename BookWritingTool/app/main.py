"""
Main entry point for BookWritingTool
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from loguru import logger

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

from app.gui.main_window import MainWindow


def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    logger.add(
        log_file,
        rotation="10 MB",
        retention="1 week",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("BookWritingTool starting...")


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("BookWritingTool")
    app.setOrganizationName("ValCore")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("Main window created and displayed")

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
