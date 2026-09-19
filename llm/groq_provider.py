"""
IntentCart - LLM Intelligence Layer
Module: llm/groq_provider.py

Objective:
Groq Cloud API provider implementation via standard HTTP client.
Supports ultra-low-latency models (llama-3.3-70b-versatile, llama-3.1-8b-instant).
Uses Groq's OpenAI-compatible /chat/completions endpoint without external SDKs.
"""

import httpx
from typing import Optional
from llm.base import LLMProvider
import llm.config as config

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.GROQ_API_KEY
        self.model = model or config.GROQ_MODEL

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self.model

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def _build_payload(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> dict:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        return {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> str:
        if not self.is_configured():
            raise ValueError("GROQ_API_KEY is not configured in .env")

        payload = self._build_payload(prompt, system_instruction, temperature, max_tokens)
        headers = self._build_headers()

        with httpx.Client(timeout=config.REQUEST_TIMEOUT_SECONDS) as client:
            resp = client.post(GROQ_ENDPOINT, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Groq API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Unexpected response format from Groq API: {data}") from e

    async def generate_text_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> str:
        if not self.is_configured():
            raise ValueError("GROQ_API_KEY is not configured in .env")

        payload = self._build_payload(prompt, system_instruction, temperature, max_tokens)
        headers = self._build_headers()

        async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(GROQ_ENDPOINT, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"Groq API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Unexpected response format from Groq API: {data}") from e
