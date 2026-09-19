"""
IntentCart - LLM Intelligence Layer
Module: llm/gemini_provider.py

Objective:
Google Gemini API provider implementation via standard HTTP client.
Supports gemini-2.5-flash and gemini-1.5-flash with low latency.
"""

import httpx
from typing import Optional
from llm.base import LLMProvider
import llm.config as config

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model = model or config.GEMINI_MODEL

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self.model

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def _build_payload(self, prompt: str, system_instruction: Optional[str], temperature: float, max_tokens: int) -> dict:
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        return payload

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> str:
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured in .env")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = self._build_payload(prompt, system_instruction, temperature, max_tokens)

        with httpx.Client(timeout=config.REQUEST_TIMEOUT_SECONDS) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Unexpected response format from Gemini API: {data}") from e

    async def generate_text_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> str:
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured in .env")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = self._build_payload(prompt, system_instruction, temperature, max_tokens)

        async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Unexpected response format from Gemini API: {data}") from e
