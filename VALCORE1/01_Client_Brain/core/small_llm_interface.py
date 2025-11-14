"""
VALCORE1 Small LLM Interface
Fallback LLM running on RTX 4070 (GPU 1)
"""

import json
import logging
import torch
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SmallLLM:
    """Small LLM for fallback when server is unavailable"""

    def __init__(self, config_path: str = "config/network_config.json"):
        """Initialize small LLM on GPU 1 (RTX 4070)"""
        self.config = self._load_config(config_path)

        # Set to GPU 1 (RTX 4070)
        if torch.cuda.is_available() and torch.cuda.device_count() > 1:
            torch.cuda.set_device(1)
            logger.info(f"Small LLM using GPU 1: {torch.cuda.get_device_name(1)}")
        else:
            logger.warning("GPU 1 not available, using available device")

        self._init_model()

    def _load_config(self, path: str) -> dict:
        """Load configuration"""
        with open(path, 'r') as f:
            return json.load(f)

    def _init_model(self):
        """Initialize the fallback model"""
        try:
            # Use Ollama for local inference
            import ollama

            model_name = self.config['fallback']['model']
            logger.info(f"Initializing fallback model: {model_name}")

            # Verify model is available
            try:
                ollama.show(model_name)
                self.model_name = model_name
                self.available = True
                logger.info(f"Fallback model ready: {model_name}")

            except Exception as e:
                logger.error(f"Fallback model not available: {e}")
                self.available = False

        except ImportError:
            logger.error("Ollama not installed - fallback unavailable")
            self.available = False

    def generate(self, prompt: str, context: str = "") -> str:
        """
        Generate response using small LLM

        Args:
            prompt: User prompt
            context: Additional context

        Returns:
            Generated text
        """
        if not self.available:
            return "Sorry Boss, the fallback LLM is not available right now."

        try:
            import ollama

            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            logger.info(f"Generating with fallback LLM: {self.model_name}")

            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options={
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            )

            return response['response']

        except Exception as e:
            logger.error(f"Fallback generation error: {e}")
            return f"Sorry Boss, fallback LLM encountered an error: {e}"
