"""
IntentCart - LLM Intelligence Layer
Module: llm/router.py

Objective:
Multi-model racing and fallback router.
Supports:
1. 'race' mode: Dispatches requests concurrently to Gemini (e.g. gemini-2.5-flash)
   and Groq (e.g. llama-3.3-70b, llama-3.1-8b). Whichever returns a valid response
   first wins, and pending requests are cancelled immediately to minimize latency.
2. 'fallback' mode: Tries providers sequentially.
3. Provider isolation: User can choose 'gemini' or 'groq'.
"""

import asyncio
import time
import logging
from typing import Optional, Tuple, List
from llm.base import LLMProvider
from llm.gemini_provider import GeminiProvider
from llm.groq_provider import GroqProvider
import llm.config as config

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        # Register candidates
        self.providers: List[LLMProvider] = []
        
        # 1. Gemini
        self.gemini = GeminiProvider(model=config.GEMINI_MODEL)
        self.providers.append(self.gemini)

        # 2. Groq Primary (e.g., Llama 3.3 70B Versatile)
        self.groq_primary = GroqProvider(model=config.GROQ_MODEL)
        self.providers.append(self.groq_primary)

        # 3. Groq Fast (e.g., Llama 3.1 8B Instant)
        if config.GROQ_FAST_MODEL and config.GROQ_FAST_MODEL != config.GROQ_MODEL:
            self.groq_fast = GroqProvider(model=config.GROQ_FAST_MODEL)
            self.providers.append(self.groq_fast)
        else:
            self.groq_fast = None

    def get_configured_providers(self) -> List[LLMProvider]:
        """Returns list of providers that have valid API keys."""
        mode = config.PROVIDER_MODE
        if mode == "gemini":
            return [p for p in self.providers if p.provider_name == "gemini" and p.is_configured()]
        elif mode == "groq":
            return [p for p in self.providers if p.provider_name == "groq" and p.is_configured()]
        else:
            return [p for p in self.providers if p.is_configured()]

    async def _execute_single(
        self,
        provider: LLMProvider,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, dict]:
        start = time.perf_counter()
        text = await provider.generate_text_async(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens
        )
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        meta = {
            "provider": provider.provider_name,
            "model": provider.model_name,
            "latency_ms": latency_ms
        }
        return text, meta

    async def generate_text_async(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = config.DEFAULT_TEMPERATURE,
        max_tokens: int = config.DEFAULT_MAX_TOKENS
    ) -> Tuple[str, dict]:
        """
        Executes generation using configured strategy ('race' or 'fallback').
        Returns tuple of (generated_text, metadata_dict).
        """
        active = self.get_configured_providers()
        if not active:
            raise RuntimeError(
                "No LLM provider is configured. Please provide at least one valid API key "
                "(GEMINI_API_KEY or GROQ_API_KEY) in your .env file."
            )

        mode = config.PROVIDER_MODE

        # Single provider configured or forced mode
        if len(active) == 1 or mode in ("gemini", "groq"):
            return await self._execute_single(active[0], prompt, system_instruction, temperature, max_tokens)

        # Race mode: Dispatch all active models concurrently, first valid finish wins!
        if mode == "race":
            tasks = [
                asyncio.create_task(
                    self._execute_single(p, prompt, system_instruction, temperature, max_tokens),
                    name=f"{p.provider_name}:{p.model_name}"
                )
                for p in active
            ]

            pending = set(tasks)
            errors = []

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    try:
                        result_text, meta = task.result()
                        if result_text and result_text.strip():
                            # Cancel remaining tasks to save tokens & rate limits
                            for remaining in pending:
                                remaining.cancel()
                            meta["race_winner"] = True
                            meta["total_racers"] = len(active)
                            return result_text, meta
                    except Exception as e:
                        errors.append(f"{task.get_name()}: {str(e)}")

            raise RuntimeError(f"All racing LLM models failed. Errors: {errors}")

        # Fallback mode: Sequential attempt
        errors = []
        for provider in active:
            try:
                text, meta = await self._execute_single(
                    provider, prompt, system_instruction, temperature, max_tokens
                )
                meta["fallback_provider"] = True
                return text, meta
            except Exception as e:
                errors.append(f"{provider.provider_name}({provider.model_name}): {str(e)}")

        raise RuntimeError(f"All fallback LLM providers failed. Errors: {errors}")

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = config.DEFAULT_TEMPERATURE,
        max_tokens: int = config.DEFAULT_MAX_TOKENS
    ) -> Tuple[str, dict]:
        """Synchronous wrapper for generate_text_async."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If inside an existing running event loop, create a new loop in a thread or task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    asyncio.run,
                    self.generate_text_async(prompt, system_instruction, temperature, max_tokens)
                )
                return future.result()
        else:
            return asyncio.run(
                self.generate_text_async(prompt, system_instruction, temperature, max_tokens)
            )

# Global router instance singleton
router = LLMRouter()
