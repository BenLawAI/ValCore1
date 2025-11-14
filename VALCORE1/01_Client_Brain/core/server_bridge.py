"""
VALCORE1 Server Bridge
Handles communication with ATOM server with retry logic and fallback
"""

import json
import logging
import time
from typing import Optional, Dict
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class ServerBridge:
    """Manages connection to ATOM server with automatic fallback"""

    def __init__(self, config_path: str = "config/network_config.json"):
        """Initialize server bridge"""
        self.config = self._load_config(config_path)
        self.server_available = False
        self.fallback_llm = None

        # Build server URL
        if self.config.get('prefer_tailscale') and self.config.get('atom_tailscale_ip'):
            host = self.config['atom_tailscale_ip']
        else:
            host = self.config['atom_local_ip']

        port = self.config['atom_port']
        self.server_url = f"http://{host}:{port}"

        logger.info(f"Server bridge initialized: {self.server_url}")

    def _load_config(self, path: str) -> dict:
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)

    def check_server_health(self) -> bool:
        """
        Ping server to check availability

        Returns:
            True if server is available
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/tags",
                timeout=5
            )
            self.server_available = (response.status_code == 200)
            return self.server_available

        except requests.exceptions.RequestException:
            self.server_available = False
            return False

    def query_llm(self, prompt: str, context: str = "", room_config: Optional[Dict] = None) -> Optional[str]:
        """
        Query server LLM with retry and fallback

        Args:
            prompt: User prompt
            context: Additional context
            room_config: Room-specific configuration (temperature, etc.)

        Returns:
            LLM response or None if failed
        """
        timeout = self.config['connection_timeout']
        max_retries = self.config['retry_attempts']
        backoff_base = self.config['retry_backoff_base']

        # Build full prompt with context
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        # Get room settings
        temperature = room_config.get('llm_temperature', 0.7) if room_config else 0.7
        max_tokens = room_config.get('max_tokens', 2000) if room_config else 2000

        # Try server with retries
        for attempt in range(max_retries):
            try:
                logger.info(f"Querying server (attempt {attempt + 1}/{max_retries})...")

                response = requests.post(
                    f"{self.server_url}/api/generate",
                    json={
                        "model": "qwen2.5:14b",
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    },
                    timeout=timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    self.server_available = True
                    return result.get('response', '')

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    sleep_time = backoff_base ** attempt
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)

            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    sleep_time = backoff_base ** attempt
                    time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Unexpected error: {e}")

        # All retries failed - fall back to local LLM
        logger.warning("Server unavailable, falling back to local LLM")
        self.server_available = False
        return self.fallback_to_small_llm(prompt, context)

    def fallback_to_small_llm(self, prompt: str, context: str = "") -> Optional[str]:
        """
        Use local small LLM on RTX 4070 when server is down

        Args:
            prompt: User prompt
            context: Additional context

        Returns:
            LLM response
        """
        if not self.config['fallback']['enabled']:
            logger.error("Fallback is disabled")
            return "Sorry Boss, I can't reach the server and fallback is disabled."

        try:
            # Initialize fallback LLM if not already done
            if self.fallback_llm is None:
                from .small_llm_interface import SmallLLM
                self.fallback_llm = SmallLLM()

            return self.fallback_llm.generate(prompt, context)

        except Exception as e:
            logger.error(f"Fallback LLM error: {e}")
            return f"Sorry Boss, I'm having trouble with both the server and local LLM: {e}"

    def get_status(self) -> Dict:
        """
        Get bridge status

        Returns:
            Status dictionary
        """
        return {
            "server_url": self.server_url,
            "server_available": self.server_available,
            "fallback_enabled": self.config['fallback']['enabled']
        }
