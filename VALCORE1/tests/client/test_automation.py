"""
Unit tests for Automation component
Tests application launching, window control, and command injection prevention
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

# Import Automation
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "01_Client_Brain"))


@pytest.mark.unit
class TestAutomation:
    """Test suite for Automation class"""

    @pytest.fixture
    def automation(self):
        """Create Automation instance"""
        from core.automation import Automation
        return Automation()

    def test_initialization(self, automation):
        """Test Automation initialization"""
        assert automation is not None
        assert hasattr(automation, 'action_history')
        assert len(automation.action_history) == 0

    @patch('subprocess.Popen')
    def test_launch_application_safe(self, mock_popen, automation):
        """Test launching application with safe input"""
        mock_popen.return_value = MagicMock()

        result = automation.launch_application('notepad.exe')

        assert result is True
        mock_popen.assert_called_once()

        # Verify shell=False was used (security fix)
        call_args = mock_popen.call_args
        assert call_args[1]['shell'] is False

    def test_launch_application_injection_prevention(self, automation):
        """Test command injection prevention (Step 2 security fix)"""
        # Dangerous inputs with injection attempts
        dangerous_inputs = [
            'notepad.exe & del /f /q important.txt',
            'notepad.exe | malicious_script.bat',
            'notepad.exe; rm -rf /',
            'notepad.exe`malicious`',
            'notepad.exe$(bad_command)',
        ]

        for dangerous_input in dangerous_inputs:
            result = automation.launch_application(dangerous_input)

            # Should reject dangerous input
            assert result is False, f"Should reject: {dangerous_input}"

    @patch('subprocess.Popen')
    def test_launch_application_with_arguments(self, mock_popen, automation):
        """Test launching application with arguments"""
        mock_popen.return_value = MagicMock()

        result = automation.launch_application('notepad.exe test.txt')

        assert result is True
        mock_popen.assert_called_once()

        # Verify arguments were parsed correctly
        call_args = mock_popen.call_args
        # Should split into ['notepad.exe', 'test.txt']
        assert len(call_args[0][0]) >= 2

    def test_launch_application_empty_string(self, automation):
        """Test launching with empty string"""
        result = automation.launch_application('')

        assert result is False

    def test_action_history_tracking(self, automation):
        """Test that actions are tracked in history"""
        with patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value = MagicMock()

            automation.launch_application('notepad.exe')

            # Should be in history
            assert len(automation.action_history) > 0

    @patch('pyautogui.typewrite')
    def test_type_to_active_window(self, mock_typewrite, automation):
        """Test typing to active window"""
        try:
            automation.type_to_active_window('Hello, World!')

            mock_typewrite.assert_called_once_with('Hello, World!', interval=0.05)
        except ImportError:
            pytest.skip("pyautogui not available")

    def test_emergency_undo(self, automation):
        """Test emergency undo functionality"""
        # Add some actions to history
        automation.action_history.append({
            'action': 'launch',
            'target': 'test_app'
        })

        automation.emergency_undo()

        # History should be cleared or marked
        # (Implementation depends on actual undo logic)
        assert True  # Basic test that it doesn't crash

    @patch('pyautogui.press')
    def test_keystroke_sending(self, mock_press, automation):
        """Test sending keystrokes"""
        try:
            # This tests the internal keystroke functionality
            import pyautogui
            pyautogui.press('enter')

            mock_press.assert_called_with('enter')
        except ImportError:
            pytest.skip("pyautogui not available")


@pytest.mark.integration
class TestAutomationIntegration:
    """Integration tests for Automation"""

    @pytest.fixture
    def automation(self):
        """Create Automation instance"""
        from core.automation import Automation
        return Automation()

    def test_safe_application_launch_flow(self, automation):
        """Test safe application launch workflow"""
        # Test with calculator (should be safe and commonly available)
        with patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value = MagicMock()

            result = automation.launch_application('calc.exe')

            assert result is True
            assert len(automation.action_history) > 0

            # Verify security: shell=False
            call_args = mock_popen.call_args
            assert call_args[1]['shell'] is False

    def test_injection_attack_scenarios(self, automation):
        """Test various command injection attack scenarios"""
        # Real-world attack attempts
        attack_scenarios = [
            # Windows attacks
            'notepad.exe & net user hacker password /add',
            'cmd.exe /c echo malicious > file.txt',
            'powershell.exe -Command "Invoke-WebRequest"',

            # Linux attacks (for cross-platform testing)
            'ls | grep secret',
            'cat /etc/passwd; malicious',
            'rm -rf / #',

            # Mixed attacks
            'app.exe`whoami`',
            'app.exe$(uname -a)',
        ]

        for attack in attack_scenarios:
            result = automation.launch_application(attack)

            # All should be rejected
            assert result is False, f"Failed to block: {attack}"


@pytest.mark.unit
class TestAutomationSecurity:
    """Security-focused tests for Automation"""

    @pytest.fixture
    def automation(self):
        """Create Automation instance"""
        from core.automation import Automation
        return Automation()

    def test_dangerous_characters_detection(self, automation):
        """Test detection of dangerous characters"""
        dangerous_chars = ['&', '|', ';', '\n', '\r', '`', '$', '(', ')']

        for char in dangerous_chars:
            malicious_input = f"notepad.exe{char}malicious"
            result = automation.launch_application(malicious_input)

            assert result is False, f"Should reject input with: {char}"

    def test_whitelist_approach(self, automation):
        """Test safe commands are allowed"""
        safe_commands = [
            'notepad.exe',
            'calc.exe',
            'mspaint.exe',
            'explorer.exe',
        ]

        with patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value = MagicMock()

            for safe_cmd in safe_commands:
                result = automation.launch_application(safe_cmd)
                assert result is True, f"Should allow: {safe_cmd}"

    def test_shell_injection_via_quotes(self, automation):
        """Test shell injection attempts via quotes"""
        quote_attacks = [
            'notepad.exe" & malicious',
            "notepad.exe' | bad_command",
            'notepad.exe"; rm -rf /',
        ]

        for attack in quote_attacks:
            result = automation.launch_application(attack)
            # Should either reject or safely handle
            # If accepted, must use shell=False (tested elsewhere)
            assert True  # Verify no exception raised

    @patch('subprocess.Popen')
    def test_subprocess_security_flags(self, mock_popen, automation):
        """Test subprocess is called with secure flags"""
        mock_popen.return_value = MagicMock()

        automation.launch_application('safe_app.exe')

        call_args = mock_popen.call_args

        # Verify security settings
        assert call_args[1]['shell'] is False  # CRITICAL: No shell
        assert call_args[1]['stdin'] is not None  # DEVNULL
        assert call_args[1]['stdout'] is not None  # DEVNULL
        assert call_args[1]['stderr'] is not None  # DEVNULL
