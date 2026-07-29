from __future__ import annotations

from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq's OpenAI-compatible Chat Completions endpoint."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            default_model="qwen/qwen3.6-27b",
        )
