"""
IntentCart - LLM Intelligence Layer
Module: llm/intent_extractor.py
"""

import json
import re
import os
import logging
from typing import Tuple
from llm.schemas import ExtractedIntentSchema, HardConstraintsSchema, SoftPreferencesSchema
from llm.router import router

logger = logging.getLogger(__name__)

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "intent_extraction_v1.txt")

def _load_system_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

SYSTEM_PROMPT = _load_system_prompt()

def _clean_json_text(raw_text: str) -> str:
    """Strips markdown code blocks, backticks, extra whitespace, and heals common JSON syntax anomalies."""
    text = raw_text.strip()
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
    
    # Find outer curly braces
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1:
        if end_idx != -1 and end_idx > start_idx:
            text = text[start_idx : end_idx + 1]
        else:
            text = text[start_idx:]

    # Strip trailing commas before closing braces/brackets (e.g. `{"a": 1,}`)
    text = re.sub(r",\s*([\]}])", r"\1", text)

    # Balance unclosed brackets/braces if truncated
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    if open_brackets > 0:
        text += "]" * open_brackets
    if open_braces > 0:
        text += "}" * open_braces

    return text


class IntentExtractor:
    def __init__(self):
        self.router = router
        self.system_prompt = SYSTEM_PROMPT

    def extract_intent(self, user_query: str) -> Tuple[ExtractedIntentSchema, dict]:
        """
        Synchronously extracts structured intent from user query.
        Returns (ExtractedIntentSchema, metadata_dict).
        """
        user_prompt = f"User Request: {user_query}\n\nExtract intent JSON:"
        raw_output, meta = self.router.generate_text(
            prompt=user_prompt,
            system_instruction=self.system_prompt,
            temperature=0.0,
            max_tokens=1024
        )

        cleaned_json = _clean_json_text(raw_output)
        try:
            parsed = json.loads(cleaned_json)
            schema_obj = ExtractedIntentSchema(**parsed)
            return schema_obj, meta
        except Exception as e:
            logger.warning(f"Failed to parse LLM intent JSON ({e}). Raw was: {raw_output[:200]}")
            # Fallback heuristic intent
            fallback_schema = self._fallback_heuristic(user_query)
            meta["schema_parse_fallback"] = True
            return fallback_schema, meta

    async def extract_intent_async(self, user_query: str) -> Tuple[ExtractedIntentSchema, dict]:
        """
        Asynchronously extracts structured intent from user query.
        Returns (ExtractedIntentSchema, metadata_dict).
        """
        user_prompt = f"User Request: {user_query}\n\nExtract intent JSON:"
        raw_output, meta = await self.router.generate_text_async(
            prompt=user_prompt,
            system_instruction=self.system_prompt,
            temperature=0.0,
            max_tokens=1024
        )

        cleaned_json = _clean_json_text(raw_output)
        try:
            parsed = json.loads(cleaned_json)
            schema_obj = ExtractedIntentSchema(**parsed)
            return schema_obj, meta
        except Exception as e:
            logger.warning(f"Failed to parse LLM intent JSON ({e}). Raw was: {raw_output[:200]}")
            fallback_schema = self._fallback_heuristic(user_query)
            meta["schema_parse_fallback"] = True
            return fallback_schema, meta

    def _fallback_heuristic(self, query: str) -> ExtractedIntentSchema:
        """Deterministic safety net if LLM JSON fails to parse."""
        q_lower = query.lower()
        hard = HardConstraintsSchema(in_stock_only=True)
        soft = SoftPreferencesSchema()

        if "kurta" in q_lower:
            hard.category = "Kurta"
        elif "shirt" in q_lower:
            hard.category = "Shirt"

        if any(w in q_lower for w in ["brother", "men", "man", "him", "groom"]):
            hard.gender = "Men"
        elif any(w in q_lower for w in ["sister", "women", "woman", "her", "bride"]):
            hard.gender = "Women"

        if "no floral" in q_lower or "without floral" in q_lower:
            hard.excluded_patterns = ["floral"]

        if "wedding" in q_lower:
            soft.occasion = "wedding"
            soft.formality = 0.9

        if "summer" in q_lower or "breathable" in q_lower:
            soft.season = "summer"
            soft.breathability = 0.9

        clean_search = re.sub(r"\b(no|without|avoid)\s+\w+", "", query, flags=re.IGNORECASE)
        clean_search = re.sub(r"[^\w\s]", "", clean_search).strip()

        return ExtractedIntentSchema(
            hard_constraints=hard,
            soft_preferences=soft,
            search_query=clean_search or query
        )

intent_extractor = IntentExtractor()
