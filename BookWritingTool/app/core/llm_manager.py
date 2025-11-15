"""
LLM Manager - Unified interface for Claude, GPT, and Ollama
Handles online/offline modes, cost tracking, and fallback chains
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import anthropic
import openai
import ollama
from loguru import logger
from datetime import datetime
from pathlib import Path


class LLMMode(Enum):
    """LLM operation mode"""

    ONLINE = "online"
    OFFLINE = "offline"


class LLMProvider(Enum):
    """Supported LLM providers"""

    CLAUDE = "claude"
    GPT = "gpt"
    OLLAMA = "ollama"


class LLMManager:
    """Unified LLM interface with cost tracking and fallback support"""

    # Pricing per million tokens (as of 2025)
    PRICING = {
        "claude-sonnet-4.5": {"input": 3.0, "output": 15.0},
        "claude-sonnet-3.5": {"input": 3.0, "output": 15.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    }

    def __init__(
        self,
        mode: LLMMode = LLMMode.ONLINE,
        claude_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        primary_provider: LLMProvider = LLMProvider.CLAUDE,
    ):
        """Initialize LLM Manager

        Args:
            mode: Online or offline mode
            claude_api_key: Anthropic API key (for online mode)
            openai_api_key: OpenAI API key (for online mode)
            ollama_base_url: Ollama server URL (for offline mode)
            primary_provider: Primary LLM provider to use first
        """
        self.mode = mode
        self.primary_provider = primary_provider
        self.ollama_base_url = ollama_base_url

        # Initialize clients
        self.claude_client = None
        self.openai_client = None

        if mode == LLMMode.ONLINE:
            if claude_api_key:
                self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
            if openai_api_key:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)

        # Usage tracking
        self.session_usage: List[Dict[str, Any]] = []

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text using configured LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Specific model to use (overrides defaults)

        Returns:
            Dict with 'text', 'provider', 'model', 'usage', 'cost'
        """
        if self.mode == LLMMode.ONLINE:
            return self._generate_online(prompt, system_prompt, max_tokens, temperature, model)
        else:
            return self._generate_offline(prompt, system_prompt, max_tokens, temperature, model)

    def _generate_online(
        self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float, model: Optional[str]
    ) -> Dict[str, Any]:
        """Generate using online providers (Claude or GPT)"""
        # Try primary provider first
        if self.primary_provider == LLMProvider.CLAUDE and self.claude_client:
            try:
                return self._call_claude(prompt, system_prompt, max_tokens, temperature, model)
            except Exception as e:
                logger.warning(f"Claude API failed: {e}. Falling back to GPT.")
                if self.openai_client:
                    return self._call_gpt(prompt, system_prompt, max_tokens, temperature, model)
                else:
                    raise

        elif self.primary_provider == LLMProvider.GPT and self.openai_client:
            try:
                return self._call_gpt(prompt, system_prompt, max_tokens, temperature, model)
            except Exception as e:
                logger.warning(f"GPT API failed: {e}. Falling back to Claude.")
                if self.claude_client:
                    return self._call_claude(prompt, system_prompt, max_tokens, temperature, model)
                else:
                    raise
        else:
            raise RuntimeError("No online LLM provider available")

    def _call_claude(
        self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float, model: Optional[str]
    ) -> Dict[str, Any]:
        """Call Claude API"""
        model = model or "claude-sonnet-4-5-20250929"

        messages = [{"role": "user", "content": prompt}]

        kwargs = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.claude_client.messages.create(**kwargs)

        # Extract response
        text = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Calculate cost
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        usage_record = {
            "timestamp": datetime.utcnow(),
            "provider": "claude",
            "model": model,
            "mode": "online",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
        }
        self.session_usage.append(usage_record)

        return {
            "text": text,
            "provider": "claude",
            "model": model,
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            "cost": cost,
        }

    def _call_gpt(
        self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float, model: Optional[str]
    ) -> Dict[str, Any]:
        """Call OpenAI GPT API"""
        model = model or "gpt-4-turbo"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.openai_client.chat.completions.create(
            model=model, messages=messages, max_tokens=max_tokens, temperature=temperature
        )

        # Extract response
        text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Calculate cost
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        usage_record = {
            "timestamp": datetime.utcnow(),
            "provider": "gpt",
            "model": model,
            "mode": "online",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
        }
        self.session_usage.append(usage_record)

        return {
            "text": text,
            "provider": "gpt",
            "model": model,
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            "cost": cost,
        }

    def _generate_offline(
        self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float, model: Optional[str]
    ) -> Dict[str, Any]:
        """Generate using local Ollama"""
        model = model or "llama3.1:8b"

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        try:
            response = ollama.generate(model=model, prompt=full_prompt, options={"temperature": temperature, "num_predict": max_tokens})

            text = response["response"]

            # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
            input_tokens = len(full_prompt) // 4
            output_tokens = len(text) // 4

            usage_record = {
                "timestamp": datetime.utcnow(),
                "provider": "ollama",
                "model": model,
                "mode": "offline",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": 0.0,  # Offline is free
            }
            self.session_usage.append(usage_record)

            return {
                "text": text,
                "provider": "ollama",
                "model": model,
                "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise RuntimeError(f"Ollama not available. Is it running at {self.ollama_base_url}?")

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD for API call"""
        # Map model name to pricing key
        pricing_key = None
        for key in self.PRICING.keys():
            if key in model:
                pricing_key = key
                break

        if not pricing_key:
            logger.warning(f"No pricing info for model {model}, estimating $0")
            return 0.0

        pricing = self.PRICING[pricing_key]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return round(input_cost + output_cost, 4)

    def get_session_cost(self) -> float:
        """Get total cost for current session"""
        return sum(record["cost_usd"] for record in self.session_usage)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_tokens = sum(record["input_tokens"] + record["output_tokens"] for record in self.session_usage)
        total_cost = self.get_session_cost()

        return {
            "total_calls": len(self.session_usage),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "mode": self.mode.value,
        }

    def switch_mode(self, mode: LLMMode):
        """Switch between online and offline modes"""
        self.mode = mode
        logger.info(f"Switched to {mode.value} mode")
