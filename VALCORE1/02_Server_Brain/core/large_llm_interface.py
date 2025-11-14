"""
VALCORE1 Large LLM Interface
Interface to Ollama for large language models on ATOM server
"""

import logging
import json
from typing import Optional, Generator, List, Dict
from pathlib import Path

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama library not available")

logger = logging.getLogger(__name__)


class LargeLLM:
    """Large LLM interface using Ollama"""

    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize large LLM interface"""
        self.config = self._load_config(config_path)

        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama library is required for LargeLLM")

        # Configure Ollama client
        self.client = ollama.Client(
            host=self.config['ollama']['base_url']
        )

        self.default_model = self.config['ollama']['default_model']

        logger.info(f"Large LLM initialized with model: {self.default_model}")

        # Verify model is available
        self._verify_model()

    def _load_config(self, path: str) -> dict:
        """
        Load configuration from JSON file with environment variable overrides

        Environment variables take precedence over JSON config values.
        """
        import os
        from pathlib import Path as PathLib

        # Load .env file if it exists
        try:
            from dotenv import load_dotenv
            env_path = PathLib(__file__).parent.parent.parent.parent / '.env'
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
        except (ImportError, Exception):
            pass  # Silently continue if .env loading fails

        # Load base configuration from JSON
        with open(path, 'r') as f:
            config = json.load(f)

        # Override with environment variables
        if os.getenv('OLLAMA_BASE_URL'):
            config['ollama']['base_url'] = os.getenv('OLLAMA_BASE_URL')
        if os.getenv('DEFAULT_LLM_MODEL'):
            config['ollama']['default_model'] = os.getenv('DEFAULT_LLM_MODEL')
        if os.getenv('LIBRARY_PATH'):
            config['library_path'] = os.getenv('LIBRARY_PATH')

        return config

    def _verify_model(self):
        """Verify default model is available"""
        try:
            models = self.get_available_models()

            if self.default_model not in models:
                logger.warning(f"Default model '{self.default_model}' not found")
                logger.info(f"Available models: {', '.join(models)}")
                logger.info(f"You may need to pull the model: ollama pull {self.default_model}")

        except Exception as e:
            logger.error(f"Error verifying model: {e}")

    def get_available_models(self) -> List[str]:
        """
        Get list of available models

        Returns:
            List of model names
        """
        try:
            response = self.client.list()
            return [model['name'] for model in response.get('models', [])]

        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []

    def check_model_loaded(self, model_name: str) -> bool:
        """
        Check if model is loaded

        Args:
            model_name: Model name

        Returns:
            True if model is available
        """
        models = self.get_available_models()
        return model_name in models

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: Optional[str] = None
    ) -> str:
        """
        Generate response using LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            model: Model name (uses default if None)

        Returns:
            Generated text
        """
        model_name = model or self.default_model

        try:
            logger.info(f"Generating with {model_name} (temp={temperature}, max_tokens={max_tokens})")

            # Build messages
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            # Generate response
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )

            result = response['message']['content']

            logger.info(f"Generated {len(result)} characters")
            return result

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error generating response: {e}"

    def stream_generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Generate response with streaming

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            model: Model name

        Yields:
            Text chunks as they're generated
        """
        model_name = model or self.default_model

        try:
            logger.info(f"Streaming generation with {model_name}")

            # Build messages
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            # Stream response
            stream = self.client.chat(
                model=model_name,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )

            for chunk in stream:
                if 'message' in chunk:
                    content = chunk['message'].get('content', '')
                    if content:
                        yield content

        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield f"Error: {e}"

    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """
        Generate a summary of text

        Args:
            text: Text to summarize
            max_length: Maximum summary length in tokens

        Returns:
            Summary text
        """
        prompt = f"""Please provide a concise summary of the following text in {max_length} tokens or less:

{text}

Summary:"""

        return self.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=max_length
        )

    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key points from text

        Args:
            text: Text to analyze
            num_points: Number of key points to extract

        Returns:
            List of key points
        """
        prompt = f"""Extract {num_points} key points from the following text. Return only the points, one per line:

{text}

Key points:"""

        response = self.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500
        )

        # Parse response into list
        points = [line.strip() for line in response.split('\n') if line.strip() and not line.strip().startswith('#')]

        return points[:num_points]
