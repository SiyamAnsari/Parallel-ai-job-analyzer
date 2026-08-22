"""
LLM Factory providing resilient ChatGroq instances with model fallbacks.
"""
import os
import logging
from typing import Optional, List
from langchain_groq import ChatGroq
from src.config import settings

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory to instantiate and manage LLM clients."""

    @staticmethod
    def get_chat_model(
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        api_key: Optional[str] = None
    ) -> ChatGroq:
        """Create a ChatGroq instance with specified model and temperature."""
        key = api_key or settings.GROQ_API_KEY
        if not key:
            raise ValueError(
                "GROQ_API_KEY is not set. Please add GROQ_API_KEY to your .env file or environment variables."
            )

        selected_model = model_name or settings.DEFAULT_MODEL
        
        try:
            return ChatGroq(
                model=selected_model,
                temperature=temperature,
                groq_api_key=key,
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                max_retries=settings.MAX_RETRIES
            )
        except Exception as e:
            logger.warning(f"Failed to instantiate model {selected_model}: {e}. Falling back to {settings.FAST_MODEL}")
            return ChatGroq(
                model=settings.FAST_MODEL,
                temperature=temperature,
                groq_api_key=key,
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                max_retries=settings.MAX_RETRIES
            )

    @staticmethod
    def get_available_models() -> List[str]:
        """Return list of supported Groq models."""
        return [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.6-27b",
            "groq/compound",
            "groq/compound-mini"
        ]

