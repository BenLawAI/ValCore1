"""
VALCORE1 Automation Module
Handles keyboard/mouse automation and screen interaction
"""

import logging
import time
from collections import deque
from typing import Optional
import pyautogui
import pygetwindow as gw

logger = logging.getLogger(__name__)

# Configure PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class Automation:
    """Handles automation of keyboard, mouse, and screen interactions"""

    def __init__(self, undo_buffer_size: int = 3, typing_interval: float = 0.02):
        """
        Initialize automation system

        Args:
            undo_buffer_size: Number of actions to keep for undo
            typing_interval: Delay between keystrokes (seconds)
        """
        self.undo_buffer = deque(maxlen=undo_buffer_size)
        self.typing_interval = typing_interval

        logger.info("Automation system initialized")

    def get_active_window(self) -> Optional[gw.Win32Window]:
        """
        Get currently active window

        Returns:
            Active window object or None
        """
        try:
            active = gw.getActiveWindow()
            if active:
                logger.debug(f"Active window: {active.title}")
            return active

        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            return None

    def type_to_active_window(self, text: str):
        """
        Type text into currently active window (NOT console)

        Args:
            text: Text to type
        """
        active_window = self.get_active_window()

        if not active_window:
            logger.warning("No active window detected")
            return

        # Don't type into console or terminal windows
        window_title_lower = active_window.title.lower()
        if any(term in window_title_lower for term in ['powershell', 'cmd', 'terminal', 'console']):
            logger.warning(f"Refusing to type into console window: {active_window.title}")
            return

        logger.info(f"Typing to window: {active_window.title}")

        # Store action for undo
        self.undo_buffer.append({
            'action': 'type',
            'text': text,
            'window': active_window.title,
            'timestamp': time.time()
        })

        # Type the text
        pyautogui.write(text, interval=self.typing_interval)

    def press_key(self, key: str, repeat: int = 1):
        """
        Press a key multiple times

        Args:
            key: Key name (e.g., 'enter', 'backspace')
            repeat: Number of times to press
        """
        logger.info(f"Pressing {key} x{repeat}")
        pyautogui.press(key, presses=repeat)

    def emergency_undo(self):
        """
        Undo last actions in buffer (emergency stop)

        Only undoes typing actions by pressing backspace
        """
        logger.warning("EMERGENCY UNDO triggered")

        for action in reversed(self.undo_buffer):
            if action['action'] == 'type':
                text_length = len(action['text'])
                logger.info(f"Undoing typing in: {action['window']} ({text_length} chars)")

                # Press backspace for each character
                pyautogui.press('backspace', presses=text_length)

        # Clear buffer after undo
        self.undo_buffer.clear()
        logger.info("Emergency undo complete")

    def take_screenshot(self, filepath: Optional[str] = None) -> str:
        """
        Take a screenshot of the screen

        Args:
            filepath: Path to save screenshot (auto-generated if None)

        Returns:
            Path to saved screenshot
        """
        if filepath is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/screenshots/screenshot_{timestamp}.png"

        logger.info(f"Taking screenshot: {filepath}")
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

        return filepath

    def read_screen_text(self) -> str:
        """
        Perform OCR on current screen using Tesseract

        Returns:
            Extracted text from screen
        """
        try:
            import pytesseract
            from PIL import Image

            logger.info("Performing OCR on screen...")

            # Take screenshot
            screenshot = pyautogui.screenshot()

            # Perform OCR
            text = pytesseract.image_to_string(screenshot)

            logger.info(f"Extracted {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"OCR error: {e}")
            return f"OCR failed: {e}"

    def launch_application(self, app_name: str) -> bool:
        """
        Launch an application (Windows only)

        SECURITY: Uses shell=False to prevent command injection attacks.
        Validates input and properly handles paths with spaces.

        Args:
            app_name: Application name or path (can include arguments)

        Returns:
            True if launched successfully, False otherwise

        Example:
            launch_application("notepad.exe")
            launch_application("C:\\Program Files\\App\\program.exe --flag")
        """
        try:
            import subprocess
            import shlex
            import os

            logger.info(f"Launching application: {app_name}")

            # Security: Validate input to prevent obvious injection attempts
            dangerous_chars = ['&', '|', ';', '\n', '\r', '`', '$', '(', ')']
            if any(char in app_name for char in dangerous_chars):
                logger.error(f"Rejected potentially dangerous application name: {app_name}")
                return False

            # Parse command line arguments safely
            # shlex.split handles quoted paths with spaces correctly
            try:
                cmd_parts = shlex.split(app_name, posix=False)  # posix=False for Windows paths
            except ValueError as e:
                logger.error(f"Failed to parse application command: {e}")
                return False

            if not cmd_parts:
                logger.error("Empty application name provided")
                return False

            # Security: Use shell=False to prevent command injection
            # Pass command as list instead of string
            subprocess.Popen(
                cmd_parts,
                shell=False,  # CRITICAL: Prevents command injection
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            logger.info(f"Successfully launched: {cmd_parts[0]}")
            return True

        except FileNotFoundError as e:
            logger.error(f"Application not found: {app_name} - {e}")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied to launch: {app_name} - {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to launch {app_name}: {e}")
            return False

    def close_active_window(self):
        """Close the currently active window"""
        active_window = self.get_active_window()

        if not active_window:
            logger.warning("No active window to close")
            return

        logger.info(f"Closing window: {active_window.title}")

        try:
            active_window.close()
        except Exception as e:
            logger.error(f"Failed to close window: {e}")
