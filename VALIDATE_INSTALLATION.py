#!/usr/bin/env python3
"""
VALCORE1 Installation Validation Script

This script checks that VALCORE1 is properly installed and configured.
Run this before attempting to start VALCORE1 for the first time.
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_directory_structure() -> Tuple[bool, List[str]]:
    """Check that all required directories exist"""
    print_header("Checking Directory Structure")

    required_dirs = [
        "VALCORE1/01_Client_Brain/core",
        "VALCORE1/01_Client_Brain/config",
        "VALCORE1/01_Client_Brain/logs",
        "VALCORE1/01_Client_Brain/models",
        "VALCORE1/02_Server_Brain/core",
        "VALCORE1/02_Server_Brain/config",
        "VALCORE1/02_Server_Brain/logs",
        "VALCORE1/03_Shared",
        "VALCORE1/04_Tools_Registry",
        "VALCORE1/04_Documentation",
        "VALCORE1/05_Setup_Scripts",
        "VALCORE1/06_Deployment",
        "Library/daily",
        "Library/monthly",
        "Library/yearly",
        "Library/backups",
        "Library/rooms",
        "00_SETUP_ASSISTANT",
    ]

    missing = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"{dir_path}")
        else:
            print_error(f"{dir_path} - MISSING")
            missing.append(dir_path)

    if not missing:
        print_info(f"All {len(required_dirs)} required directories found")
        return True, []
    else:
        print_warning(f"{len(missing)} directories missing")
        return False, missing

def check_python_modules() -> Tuple[bool, List[str]]:
    """Check that all Python modules are present"""
    print_header("Checking Python Modules")

    required_modules = [
        "VALCORE1/01_Client_Brain/main_client.py",
        "VALCORE1/01_Client_Brain/core/voice_system_unified.py",
        "VALCORE1/01_Client_Brain/core/server_bridge.py",
        "VALCORE1/01_Client_Brain/core/automation.py",
        "VALCORE1/01_Client_Brain/core/system_tray.py",
        "VALCORE1/01_Client_Brain/core/health_monitor.py",
        "VALCORE1/01_Client_Brain/core/emergency_stop.py",
        "VALCORE1/01_Client_Brain/core/network_fallback.py",
        "VALCORE1/01_Client_Brain/core/small_llm_interface.py",
        "VALCORE1/02_Server_Brain/main_server.py",
        "VALCORE1/02_Server_Brain/core/large_llm_interface.py",
        "VALCORE1/02_Server_Brain/core/librarian.py",
        "VALCORE1/02_Server_Brain/core/memory_compression.py",
        "VALCORE1/02_Server_Brain/core/room_manager.py",
        "VALCORE1/02_Server_Brain/core/client_bridge.py",
        "VALCORE1/03_Shared/network_protocol.py",
        "VALCORE1/03_Shared/common_utils.py",
        "VALCORE1/03_Shared/performance_profiler.py",
    ]

    missing = []
    for module_path in required_modules:
        if Path(module_path).exists():
            print_success(f"{module_path}")
        else:
            print_error(f"{module_path} - MISSING")
            missing.append(module_path)

    if not missing:
        print_info(f"All {len(required_modules)} Python modules found")
        return True, []
    else:
        print_warning(f"{len(missing)} modules missing")
        return False, missing

def check_config_files() -> Tuple[bool, List[str]]:
    """Check that all configuration files are present and valid JSON"""
    print_header("Checking Configuration Files")

    config_files = [
        "VALCORE1/01_Client_Brain/config/gpu_config.json",
        "VALCORE1/01_Client_Brain/config/network_config.json",
        "VALCORE1/01_Client_Brain/config/voice_config.json",
        "VALCORE1/01_Client_Brain/config/room_contexts.json",
        "VALCORE1/01_Client_Brain/config/settings.json",
        "VALCORE1/02_Server_Brain/config/compression_strategy.json",
        "VALCORE1/02_Server_Brain/config/compression_schedule.json",
        "VALCORE1/02_Server_Brain/config/gpu_config.json",
        "VALCORE1/02_Server_Brain/config/settings.json",
    ]

    issues = []
    for config_path in config_files:
        if not Path(config_path).exists():
            print_error(f"{config_path} - MISSING")
            issues.append(config_path)
            continue

        try:
            with open(config_path, 'r') as f:
                json.load(f)
            print_success(f"{config_path}")
        except json.JSONDecodeError as e:
            print_error(f"{config_path} - INVALID JSON: {e}")
            issues.append(config_path)

    if not issues:
        print_info(f"All {len(config_files)} config files valid")
        return True, []
    else:
        print_warning(f"{len(issues)} config files have issues")
        return False, issues

def check_requirements_files() -> Tuple[bool, List[str]]:
    """Check that requirements files exist"""
    print_header("Checking Requirements Files")

    req_files = [
        "VALCORE1/requirements.txt",
        "VALCORE1/01_Client_Brain/setup/requirements_client.txt",
        "VALCORE1/02_Server_Brain/setup/requirements_server.txt",
    ]

    missing = []
    for req_path in req_files:
        if Path(req_path).exists():
            print_success(f"{req_path}")
        else:
            print_error(f"{req_path} - MISSING")
            missing.append(req_path)

    if not missing:
        print_info(f"All {len(req_files)} requirements files found")
        return True, []
    else:
        print_warning(f"{len(missing)} requirements files missing")
        return False, missing

def check_api_keys() -> Tuple[bool, List[str]]:
    """Check if API keys are configured"""
    print_header("Checking API Keys Configuration")

    issues = []

    # Check voice config for Picovoice key
    voice_config_path = "VALCORE1/01_Client_Brain/config/voice_config.json"
    if Path(voice_config_path).exists():
        with open(voice_config_path, 'r') as f:
            voice_config = json.load(f)
            access_key = voice_config.get('wake_word', {}).get('access_key', '')

            if access_key == "YOUR_PICOVOICE_ACCESS_KEY_HERE" or not access_key:
                print_warning("Picovoice access key not configured")
                print_info("  Get your free key from: https://console.picovoice.ai/")
                print_info("  Update: VALCORE1/01_Client_Brain/config/voice_config.json")
                issues.append("Picovoice access key")
            else:
                print_success("Picovoice access key configured")

    # Check for .env file
    if Path(".env").exists():
        print_success(".env file found")
    else:
        print_warning(".env file not found (optional)")
        print_info("  Copy .env.example to .env if you need environment variables")

    if issues:
        print_warning(f"{len(issues)} API key(s) not configured (system may have limited functionality)")
        return False, issues
    else:
        print_info("All critical API keys configured")
        return True, []

def check_startup_scripts() -> Tuple[bool, List[str]]:
    """Check that startup scripts exist"""
    print_header("Checking Startup Scripts")

    scripts = [
        ("VALCORE1/START_VALCORE1.bat", "Windows client startup"),
        ("VALCORE1/02_Server_Brain/START_SERVER.sh", "Linux server startup"),
    ]

    missing = []
    for script_path, description in scripts:
        if Path(script_path).exists():
            print_success(f"{description}: {script_path}")
        else:
            print_error(f"{description}: {script_path} - MISSING")
            missing.append(script_path)

    if not missing:
        print_info(f"All startup scripts found")
        return True, []
    else:
        print_warning(f"{len(missing)} startup scripts missing")
        return False, missing

def main():
    """Run all validation checks"""
    print(f"\n{Colors.BOLD}VALCORE1 Installation Validator{Colors.END}")
    print(f"{Colors.BOLD}Version 1.0{Colors.END}\n")

    checks = [
        ("Directory Structure", check_directory_structure),
        ("Python Modules", check_python_modules),
        ("Configuration Files", check_config_files),
        ("Requirements Files", check_requirements_files),
        ("API Keys", check_api_keys),
        ("Startup Scripts", check_startup_scripts),
    ]

    results = []
    all_issues = []

    for check_name, check_func in checks:
        passed, issues = check_func()
        results.append((check_name, passed))
        if issues:
            all_issues.extend([(check_name, issue) for issue in issues])

    # Print summary
    print_header("Validation Summary")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for check_name, passed in results:
        if passed:
            print_success(f"{check_name}")
        else:
            print_warning(f"{check_name} - Has issues")

    print(f"\n{Colors.BOLD}Result: {passed_count}/{total_count} checks passed{Colors.END}\n")

    if all_issues:
        print_header("Issues Found")
        for check_name, issue in all_issues:
            print(f"{Colors.YELLOW}[{check_name}]{Colors.END} {issue}")
        print()

    # Final verdict
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ VALCORE1 installation is valid and ready to use!{Colors.END}\n")
        print_info("Next steps:")
        print_info("  1. Review 00_SETUP_ASSISTANT/00_READ_ME_FIRST.md")
        print_info("  2. Follow Phase 2 setup with Val (Sonnet 4.5)")
        print_info("  3. Run diagnostic tests before first use")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ VALCORE1 installation has some issues{Colors.END}\n")
        print_info("The system may still work, but some features could be limited.")
        print_info("Review the issues above and fix critical ones before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
