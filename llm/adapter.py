"""
IntentCart - LLM Intelligence Layer
Module: llm/adapter.py

Objective:
Bridges the LLM's ExtractedIntentSchema with the deterministic ML IntentCartPipeline.
Translates structured Pydantic intent objects into exact parameters for
retrieval and hybrid scoring without altering the underlying ML engine.
"""

from typing import Any, Dict
from llm.schemas import ExtractedIntentSchema

def map_schema_to_pipeline_args(schema: ExtractedIntentSchema) -> Dict[str, Any]:
    """
    Transforms ExtractedIntentSchema into kwargs for IntentCartPipeline.run().
    """
    # 1. Hard Constraints: Filter out None values and empty lists
    raw_hard = schema.hard_constraints.model_dump()
    hard_constraints = {}
    for k, v in raw_hard.items():
        if v is not None:
            if isinstance(v, list) and len(v) == 0:
                continue
            hard_constraints[k] = v

    # 2. Soft Intent: Map continuous weights and attributes to keyword preference tags
    soft_dump = schema.soft_preferences.model_dump()
    prefs = []
    if soft_dump.get("breathability", 0.0) >= 0.6:
        prefs.append("breathable")
    if soft_dump.get("minimalism", 0.0) >= 0.6:
        prefs.append("minimal")
    if soft_dump.get("comfort", 0.0) >= 0.6:
        prefs.append("comfortable")
    if soft_dump.get("formality", 0.0) >= 0.6:
        prefs.append("formal")

    # Add preferred materials/colors to preference tags
    prefs.extend(soft_dump.get("preferred_materials", []))
    prefs.extend(soft_dump.get("preferred_colors", []))

    soft_intent = {
        "preferences": list(dict.fromkeys(prefs)), # Deduplicate preserving order
        "occasion": soft_dump.get("occasion"),
        "season": soft_dump.get("season")
    }

    return {
        "query": schema.search_query,
        "hard_constraints": hard_constraints,
        "soft_intent": soft_intent
    }
