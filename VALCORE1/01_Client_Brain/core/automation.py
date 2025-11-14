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

    def launch_application(self, app_name: str):
        """
        Launch an application (Windows only)

        Args:
            app_name: Application name or path
        """
        try:
            import subprocess
            import shlex
            import os

            logger.info(f"Launching application: {app_name}")

            # Security: Validate input - no shell metacharacters allowed
            dangerous_chars = ['&', '|', ';', '$', '`', '\n', '>', '<', '(', ')']
            if any(char in app_name for char in dangerous_chars):
                logger.error(f"Rejected application launch - dangerous characters detected: {app_name}")
                raise ValueError("Application name contains potentially dangerous characters")

            # Security: Use shell=False to prevent command injection
            # Split command properly if it contains arguments
            if os.name == 'nt':  # Windows
                # On Windows, pass as string but without shell=True for simple commands
                # Or split if it's a path with spaces
                subprocess.Popen(app_name, shell=False)
            else:  # Unix-like
                # On Unix, properly split the command
                args = shlex.split(app_name)
                subprocess.Popen(args, shell=False)

        except ValueError as ve:
            logger.error(f"Security violation when launching {app_name}: {ve}")
            raise
        except Exception as e:
            logger.error(f"Failed to launch {app_name}: {e}")

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
