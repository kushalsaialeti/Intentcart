"""
IntentCart - LLM Intelligence Layer
Module: llm/explainer.py

Objective:
Generates natural, grounded conversational explanations and styling summaries
based strictly on verified ML pipeline results and candidate evidence tokens.
Zero hallucination of prices, materials, or brands.
"""

import os
from typing import Any, Dict, Tuple
from llm.router import router
from llm.evidence_builder import build_explainer_context

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "explanation_v1.txt")

def _load_system_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

SYSTEM_PROMPT = _load_system_prompt()

class GroundedExplainer:
    def __init__(self):
        self.router = router
        self.system_prompt = SYSTEM_PROMPT

    def explain_recommendations(
        self,
        user_query: str,
        hard_constraints: Dict[str, Any],
        soft_intent: Dict[str, Any],
        pipeline_output: Dict[str, Any]
    ) -> Tuple[str, dict]:
        """
        Synchronously generates conversational explanation for recommended products.
        Returns (explanation_text, metadata_dict).
        """
        grounded_context = build_explainer_context(
            user_query, hard_constraints, soft_intent, pipeline_output
        )
        prompt = f"Please explain these recommendations for the user:\n\n{grounded_context}"

        text, meta = self.router.generate_text(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=0.3,
            max_tokens=1024
        )
        return text, meta

    async def explain_recommendations_async(
        self,
        user_query: str,
        hard_constraints: Dict[str, Any],
        soft_intent: Dict[str, Any],
        pipeline_output: Dict[str, Any]
    ) -> Tuple[str, dict]:
        """
        Asynchronously generates conversational explanation for recommended products.
        Returns (explanation_text, metadata_dict).
        """
        grounded_context = build_explainer_context(
            user_query, hard_constraints, soft_intent, pipeline_output
        )
        prompt = f"Please explain these recommendations for the user:\n\n{grounded_context}"

        text, meta = await self.router.generate_text_async(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=0.3,
            max_tokens=1024
        )
        return text, meta

grounded_explainer = GroundedExplainer()
