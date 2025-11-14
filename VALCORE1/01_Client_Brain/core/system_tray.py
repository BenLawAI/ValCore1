"""
VALCORE1 System Tray
Windows system tray integration with status indicators
"""

import logging
import threading
from typing import Optional
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

logger = logging.getLogger(__name__)


class SystemTray:
    """Manages Windows system tray icon and menu"""

    def __init__(self, voice_system, server_bridge, health_monitor):
        """
        Initialize system tray

        Args:
            voice_system: Reference to VALVoiceSystem
            server_bridge: Reference to ServerBridge
            health_monitor: Reference to HealthMonitor
        """
        self.voice_system = voice_system
        self.server_bridge = server_bridge
        self.health_monitor = health_monitor

        self.icon = None
        self.status = "listening"  # listening, processing, error, disabled
        self.thread = None

        logger.info("System tray initialized")

    def create_icon(self, color: str) -> Image.Image:
        """
        Create icon image with specified color

        Args:
            color: Color name ("green", "yellow", "red", "gray")

        Returns:
            PIL Image
        """
        # Create 64x64 icon
        size = 64
        image = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(image)

        # Color mapping
        colors = {
            'green': '#00FF00',
            'yellow': '#FFFF00',
            'red': '#FF0000',
            'gray': '#808080'
        }

        fill_color = colors.get(color, '#808080')

        # Draw circle
        draw.ellipse([8, 8, size-8, size-8], fill=fill_color, outline='black', width=2)

        # Draw "V" for Val
        draw.text((size//2 - 10, size//2 - 12), "V", fill='black')

        return image

    def get_status_color(self) -> str:
        """
        Get icon color based on system status

        Returns:
            Color name
        """
        if not self.voice_system.microphone_enabled:
            return 'gray'
        elif self.status == 'error':
            return 'red'
        elif self.status == 'processing':
            return 'yellow'
        else:
            return 'green'

    def update_status(self, status: str):
        """
        Update system status and icon

        Args:
            status: Status string ("listening", "processing", "error", "disabled")
        """
        self.status = status
        if self.icon:
            color = self.get_status_color()
            self.icon.icon = self.create_icon(color)
            logger.debug(f"Status updated: {status} ({color})")

    def toggle_microphone(self, icon=None, item=None):
        """Toggle microphone on/off"""
        state = self.voice_system.toggle_microphone()
        self.update_status('disabled' if not state else 'listening')
        logger.info(f"Microphone toggled: {'enabled' if state else 'disabled'}")

    def show_status(self, icon=None, item=None):
        """Show current system status"""
        server_status = self.server_bridge.get_status()
        health_status = self.health_monitor.get_status()

        status_msg = f"""VALCORE1 Status

Microphone: {'Enabled' if self.voice_system.microphone_enabled else 'Disabled'}
Server: {'Connected' if server_status['server_available'] else 'Disconnected'}
Server URL: {server_status['server_url']}

GPU 0 Temp: {health_status.get('gpu0_temp', 'N/A')}°C
GPU 1 Temp: {health_status.get('gpu1_temp', 'N/A')}°C
RAM Usage: {health_status.get('ram_usage', 'N/A')}%
"""
        logger.info(status_msg)
        # In production, this would show a notification or dialog

    def exit_application(self, icon=None, item=None):
        """Exit VALCORE1"""
        logger.info("Exit requested from system tray")
        if self.icon:
            self.icon.stop()
        # Signal main application to exit
        import sys
        sys.exit(0)

    def create_menu(self) -> pystray.Menu:
        """
        Create system tray menu

        Returns:
            pystray.Menu object
        """
        return pystray.Menu(
            item(
                'Microphone',
                self.toggle_microphone,
                checked=lambda item: self.voice_system.microphone_enabled
            ),
            item('Status', self.show_status),
            pystray.Menu.SEPARATOR,
            item('Exit', self.exit_application)
        )

    def start(self):
        """Start system tray in background thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("System tray already running")
            return

        def run_tray():
            color = self.get_status_color()
            self.icon = pystray.Icon(
                "VALCORE1",
                self.create_icon(color),
                "VALCORE1 - AI Voice Assistant",
                self.create_menu()
            )
            self.icon.run()

        self.thread = threading.Thread(target=run_tray, daemon=True)
        self.thread.start()
        logger.info("System tray started")

    def stop(self):
        """Stop system tray"""
        if self.icon:
            self.icon.stop()
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("System tray stopped")
