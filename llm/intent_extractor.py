"""
IntentCart - LLM Intelligence Layer
Module: llm/intent_extractor.py
"""

import json
import re
import os
import logging
from typing import Tuple, Any, Optional, Dict, List
from llm.schemas import ExtractedIntentSchema, HardConstraintsSchema, SoftPreferencesSchema
from llm.router import router
from retrieval.category_normalizer import normalize_to_canonical_category, extract_category_from_query

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

    # Strip trailing commas before closing braces/brackets
    text = re.sub(r",\s*([\]}])", r"\1", text)

    # Balance unclosed brackets/braces if truncated
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    if open_brackets > 0:
        text += "]" * open_brackets
    if open_braces > 0:
        text += "}" * open_braces

    return text


def _sanitize_raw_intent_dict(data: Any, user_query: str) -> dict:
    if not isinstance(data, dict):
        return {}

    # 1. hard_constraints
    hc = data.get("hard_constraints")
    if not isinstance(hc, dict):
        hc = {}
        data["hard_constraints"] = hc
    for k in ["gender", "category", "canonical_category"]:
        val = hc.get(k)
        if isinstance(val, list):
            hc[k] = str(val[0]) if val else None
        elif val is not None:
            hc[k] = str(val).strip() or None

    # 2. soft_preferences
    sp = data.get("soft_preferences")
    if not isinstance(sp, dict):
        sp = {}
        data["soft_preferences"] = sp
    for k in ["occasion", "season"]:
        val = sp.get(k)
        if isinstance(val, list):
            sp[k] = str(val[0]) if val else None
        elif val is not None:
            sp[k] = str(val).strip() or None

    # 3. search_query
    sq = data.get("search_query")
    if isinstance(sq, list):
        data["search_query"] = " ".join(str(x) for x in sq) if sq else user_query
    elif not sq or not isinstance(sq, str) or not sq.strip():
        data["search_query"] = user_query

    return data


# Explicit regex to identify when user specified gender
MALE_GENDER_PATTERN = r"\b(men|man|mens|men's|boys|boy's|brother|groom|father|him|his|gentlemen|male)\b"
FEMALE_GENDER_PATTERN = r"\b(women|woman|womens|women's|girls|girl's|sister|bride|mother|her|hers|ladies|female)\b"


def _post_process_intent(schema: ExtractedIntentSchema, query: str) -> ExtractedIntentSchema:
    """
    Enforces deterministic safety invariants onto the LLM output:
    1. Gender Invariant: NEVER infer gender if query lacks explicit gender words.
    2. Category Invariant: Canonical category mapping and priority.
    3. Negative constraints compilation.
    """
    q_lower = query.lower()
    hard = schema.hard_constraints

    # 1. Gender Invariant check
    has_male = bool(re.search(MALE_GENDER_PATTERN, q_lower))
    has_female = bool(re.search(FEMALE_GENDER_PATTERN, q_lower))

    if has_male and not has_female:
        hard.gender = "Men"
        hard.gender_specified = True
    elif has_female and not has_male:
        hard.gender = "Women"
        hard.gender_specified = True
    elif not has_male and not has_female:
        # Category-implied female exceptions (e.g. 'dress', 'gown')
        detected_cat = extract_category_from_query(query)
        if detected_cat == "Dresses":
            hard.gender = "Women"
            hard.gender_specified = True
        else:
            # Strictly unspecified - OVERRIDE any hallucinated gender
            hard.gender = None
            hard.gender_specified = False

    # 2. Canonical Category Invariant check
    query_category = extract_category_from_query(query)
    if query_category:
        hard.canonical_category = query_category
        hard.category = query_category.rstrip("s") # singular display form
    elif hard.category:
        canonical = normalize_to_canonical_category(hard.category)
        if canonical:
            hard.canonical_category = canonical
            hard.category = canonical.rstrip("s")
        else:
            hard.canonical_category = None

    # 3. Negative Constraints Compilation
    neg_list = list(hard.negative_constraints or [])
    for p in hard.excluded_patterns:
        neg = f"no {p}"
        if neg not in neg_list:
            neg_list.append(neg)
    for m in hard.excluded_materials:
        neg = f"no {m}"
        if neg not in neg_list:
            neg_list.append(neg)
    for c in hard.excluded_colors:
        neg = f"no {c}"
        if neg not in neg_list:
            neg_list.append(neg)
            
    # Check for direct 'no X' patterns in query
    neg_matches = re.findall(r"\b(?:no|without|avoid)\s+([a-zA-Z]+)\b", q_lower)
    for nm in neg_matches:
        neg = f"no {nm}"
        if neg not in neg_list:
            neg_list.append(neg)
        if nm in ["floral", "stripes", "striped", "print", "printed", "check", "checked"] and nm not in hard.excluded_patterns:
            hard.excluded_patterns.append(nm)

    hard.negative_constraints = neg_list

    return schema


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
        try:
            raw_output, meta = self.router.generate_text(
                prompt=user_prompt,
                system_instruction=self.system_prompt,
                temperature=0.0,
                max_tokens=1024
            )
            cleaned_json = _clean_json_text(raw_output)
            parsed = json.loads(cleaned_json)
            parsed = _sanitize_raw_intent_dict(parsed, user_query)
            schema_obj = ExtractedIntentSchema(**parsed)
            schema_obj = _post_process_intent(schema_obj, user_query)
            return schema_obj, meta
        except Exception as e:
            logger.warning(f"Failed to extract intent via LLM ({e}). Using deterministic fallback.")
            fallback_schema = self._fallback_heuristic(user_query)
            return fallback_schema, {
                "provider": "deterministic_fallback",
                "model": "rule_based",
                "latency_ms": 1.0,
                "error": str(e)
            }

    async def extract_intent_async(self, user_query: str) -> Tuple[ExtractedIntentSchema, dict]:
        """
        Asynchronously extracts structured intent from user query.
        Returns (ExtractedIntentSchema, metadata_dict).
        """
        user_prompt = f"User Request: {user_query}\n\nExtract intent JSON:"
        try:
            raw_output, meta = await self.router.generate_text_async(
                prompt=user_prompt,
                system_instruction=self.system_prompt,
                temperature=0.0,
                max_tokens=1024
            )
            cleaned_json = _clean_json_text(raw_output)
            parsed = json.loads(cleaned_json)
            parsed = _sanitize_raw_intent_dict(parsed, user_query)
            schema_obj = ExtractedIntentSchema(**parsed)
            schema_obj = _post_process_intent(schema_obj, user_query)
            return schema_obj, meta
        except Exception as e:
            logger.warning(f"Failed to extract intent async via LLM ({e}). Using deterministic fallback.")
            fallback_schema = self._fallback_heuristic(user_query)
            return fallback_schema, {
                "provider": "deterministic_fallback",
                "model": "rule_based",
                "latency_ms": 1.0,
                "error": str(e)
            }

    def _fallback_heuristic(self, query: str) -> ExtractedIntentSchema:
        """Deterministic safety net if LLM JSON fails to parse."""
        q_lower = query.lower()
        hard = HardConstraintsSchema(in_stock_only=True)
        soft = SoftPreferencesSchema()

        # Category detection via canonical normalizer
        detected_cat = extract_category_from_query(query)
        if detected_cat:
            hard.canonical_category = detected_cat
            hard.category = detected_cat.rstrip("s")

        # Gender detection
        has_male = bool(re.search(MALE_GENDER_PATTERN, q_lower))
        has_female = bool(re.search(FEMALE_GENDER_PATTERN, q_lower))

        if has_male and not has_female:
            hard.gender = "Men"
            hard.gender_specified = True
        elif has_female and not has_male:
            hard.gender = "Women"
            hard.gender_specified = True
        elif detected_cat == "Dresses":
            hard.gender = "Women"
            hard.gender_specified = True
        else:
            hard.gender = None
            hard.gender_specified = False

        # Exclusions
        if "no floral" in q_lower or "without floral" in q_lower:
            hard.excluded_patterns = ["floral"]

        # Budget extraction (e.g. under 3000, under 1500)
        budget_match = re.search(r"\b(?:under|below|less than|max)\s*(?:rs\.?|inr|₹)?\s*(\d+)", q_lower)
        if budget_match:
            try:
                hard.max_price = float(budget_match.group(1))
            except ValueError:
                pass

        if "wedding" in q_lower:
            soft.occasion = "wedding"
            soft.formality = 0.9

        if "interview" in q_lower or "office" in q_lower or "formal" in q_lower:
            soft.occasion = "formal"
            soft.formality = 0.9

        if "summer" in q_lower or "breathable" in q_lower:
            soft.season = "summer"
            soft.breathability = 0.9

        if "minimal" in q_lower or "clean" in q_lower:
            soft.minimalism = 0.9

        clean_search = re.sub(r"\b(no|without|avoid)\s+\w+", "", query, flags=re.IGNORECASE)
        clean_search = re.sub(r"[^\w\s]", "", clean_search).strip()

        schema = ExtractedIntentSchema(
            hard_constraints=hard,
            soft_preferences=soft,
            search_query=clean_search or query
        )
        return _post_process_intent(schema, query)

intent_extractor = IntentExtractor()
