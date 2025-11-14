"""
VALCORE1 Automation Module
Handles keyboard/mouse automation and screen interaction
"""

import logging
import time
import subprocess
from collections import deque
from typing import Optional, Dict
from pathlib import Path
import pyautogui
import pygetwindow as gw

# Import constants and exceptions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_Shared"))
from constants import (
    TYPING_INTERVAL_SEC,
    UNDO_BUFFER_SIZE,
    AUTOMATION_FAILSAFE,
    AUTOMATION_PAUSE_SEC,
    ALLOWED_APPLICATIONS,
    BLOCKED_WINDOW_KEYWORDS
)
from exceptions import SecurityViolationException, ApplicationLaunchException

logger = logging.getLogger(__name__)

# Configure PyAutoGUI with constants
pyautogui.FAILSAFE = AUTOMATION_FAILSAFE
pyautogui.PAUSE = AUTOMATION_PAUSE_SEC


class Automation:
    """Handles automation of keyboard, mouse, and screen interactions"""

    def __init__(self, undo_buffer_size: int = UNDO_BUFFER_SIZE, typing_interval: float = TYPING_INTERVAL_SEC):
        """
        Initialize automation system

        Args:
            undo_buffer_size: Number of actions to keep for undo (default from constants)
            typing_interval: Delay between keystrokes in seconds (default from constants)
        """
        self.undo_buffer = deque(maxlen=undo_buffer_size)
        self.typing_interval = typing_interval
        self.allowed_apps = ALLOWED_APPLICATIONS
        self.blocked_windows = BLOCKED_WINDOW_KEYWORDS

        logger.info(f"Automation system initialized (buffer size: {undo_buffer_size}, typing interval: {typing_interval}s)")

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

        # Security: Don't type into console or terminal windows
        window_title_lower = active_window.title.lower()
        if any(keyword in window_title_lower for keyword in self.blocked_windows):
            logger.warning(f"SECURITY: Refusing to type into blocked window: {active_window.title}")
            raise SecurityViolationException(f"Cannot type into blocked window type: {active_window.title}")


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
        Launch an application from ALLOWED whitelist (Windows only)

        Args:
            app_name: Application name (must be in whitelist)

        Raises:
            SecurityViolationException: If app not in whitelist
            ApplicationLaunchException: If launch fails

        Security:
            Only applications in ALLOWED_APPLICATIONS whitelist can be launched.
            This prevents command injection attacks via LLM-generated app names.
        """
        # Normalize app name
        app_name_lower = app_name.lower().strip()

        # Security check: app must be in whitelist
        if app_name_lower not in self.allowed_apps:
            logger.error(f"SECURITY: Attempted to launch unauthorized app: {app_name}")
            raise SecurityViolationException(
                f"Application '{app_name}' not in allowed list. "
                f"Allowed apps: {list(self.allowed_apps.keys())}"
            )

        try:
            app_path = self.allowed_apps[app_name_lower]
            logger.info(f"Launching allowed application: {app_name} -> {app_path}")

            # Security: NEVER use shell=True with user input
            # Expand environment variables safely
            import os
            expanded_path = os.path.expandvars(app_path)

            # Launch without shell (prevents injection)
            subprocess.Popen([expanded_path], shell=False)

            logger.info(f"Successfully launched: {app_name}")

        except FileNotFoundError:
            error_msg = f"Application executable not found: {app_path}"
            logger.error(error_msg)
            raise ApplicationLaunchException(error_msg)

        except Exception as e:
            error_msg = f"Failed to launch {app_name}: {e}"
            logger.error(error_msg)
            raise ApplicationLaunchException(error_msg) from e

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
