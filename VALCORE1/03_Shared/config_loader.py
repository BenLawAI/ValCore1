"""
VALCORE1 Configuration Loader
Loads configuration from environment variables with fallback to config files
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load configuration from environment variables and config files"""

    @staticmethod
    def load_env_file(env_path: str = ".env"):
        """
        Load environment variables from .env file

        Args:
            env_path: Path to .env file
        """
        env_file = Path(env_path)

        if not env_file.exists():
            logger.info(f".env file not found at {env_path}")
            return

        logger.info(f"Loading environment variables from {env_path}")

        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Parse key=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

            logger.info("Environment variables loaded successfully")

        except Exception as e:
            logger.error(f"Error loading .env file: {e}")

    @staticmethod
    def get_env(key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get environment variable with optional default

        Args:
            key: Environment variable name
            default: Default value if not found
            required: Raise error if not found and required=True

        Returns:
            Environment variable value or default

        Raises:
            ValueError: If required=True and variable not found
        """
        value = os.getenv(key, default)

        if required and value is None:
            raise ValueError(f"Required environment variable '{key}' not found")

        return value

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """
        Get boolean environment variable

        Args:
            key: Environment variable name
            default: Default value

        Returns:
            Boolean value
        """
        value = os.getenv(key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """
        Get integer environment variable

        Args:
            key: Environment variable name
            default: Default value

        Returns:
            Integer value
        """
        value = os.getenv(key, str(default))
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer for {key}: {value}, using default {default}")
            return default

    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """
        Get float environment variable

        Args:
            key: Environment variable name
            default: Default value

        Returns:
            Float value
        """
        value = os.getenv(key, str(default))
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float for {key}: {value}, using default {default}")
            return default

    @staticmethod
    def get_list(key: str, default: Optional[list] = None, separator: str = ',') -> list:
        """
        Get list environment variable (comma-separated by default)

        Args:
            key: Environment variable name
            default: Default value
            separator: Separator character

        Returns:
            List of values
        """
        if default is None:
            default = []

        value = os.getenv(key)
        if not value:
            return default

        return [item.strip() for item in value.split(separator) if item.strip()]

    @staticmethod
    def load_config_with_env(config_path: str, env_prefix: str = "") -> Dict:
        """
        Load JSON config file with environment variable overrides

        Args:
            config_path: Path to JSON config file
            env_prefix: Prefix for environment variables (e.g., "VALCORE_")

        Returns:
            Configuration dictionary
        """
        # Load base config from file
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Override with environment variables if present
        # This allows env vars like VALCORE_SERVER_HOST to override config['server']['host']
        def override_nested(obj: Dict, prefix: str = ""):
            for key, value in obj.items():
                env_key = f"{env_prefix}{prefix}{key}".upper()

                if isinstance(value, dict):
                    # Recursively override nested dicts
                    override_nested(value, f"{prefix}{key}_")
                else:
                    # Check for environment variable override
                    if env_key in os.environ:
                        env_value = os.getenv(env_key)

                        # Try to preserve type
                        if isinstance(value, bool):
                            obj[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                        elif isinstance(value, int):
                            try:
                                obj[key] = int(env_value)
                            except ValueError:
                                logger.warning(f"Invalid int for {env_key}: {env_value}")
                        elif isinstance(value, float):
                            try:
                                obj[key] = float(env_value)
                            except ValueError:
                                logger.warning(f"Invalid float for {env_key}: {env_value}")
                        else:
                            obj[key] = env_value

                        logger.info(f"Config override: {key} from {env_key}")

        override_nested(config)
        return config


# Convenience function for loading .env on import
def init_config(env_path: str = ".env"):
    """
    Initialize configuration by loading .env file

    Args:
        env_path: Path to .env file
    """
    # Try to load from project root
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / env_path

    if env_file.exists():
        ConfigLoader.load_env_file(str(env_file))
    else:
        # Try current directory
        ConfigLoader.load_env_file(env_path)
