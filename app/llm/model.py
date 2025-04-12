import logging
from functools import lru_cache
import os
import requests
from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MistralLLM(LLM):
    api_key: str
    model_name: str = "mistral-small"
    temperature: float = 0.7
    max_tokens: int = 500

    @property
    def _llm_type(self) -> str:
        return "mistral"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Fix the payload structure for chat completions
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        # Add stop sequences if provided
        if stop:
            data["stop"] = stop

        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            # Extract the content from response format
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling Mistral API: {e}")
            raise

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


@lru_cache()
def get_llm_model():
    api_key = os.environ.get("MISTRAL_API_KEY", "v1gJpcCMIjJSXTBCcxO8GjmzhknuCMBt")
    if not api_key:
        logger.error("API key not found")
        raise ValueError("API key not set")

    logger.info(f"Creating Mistral LLM client")
    return MistralLLM(
        api_key=api_key,
        model_name=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_NEW_TOKENS
    )