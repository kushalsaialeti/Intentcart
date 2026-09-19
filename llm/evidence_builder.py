"""
IntentCart - LLM Intelligence Layer
Module: llm/evidence_builder.py

Objective:
Compiles strictly factual, grounded evidence payloads from the ML pipeline output.
Ensures the Explainer LLM receives ONLY verified product metadata, score breakdowns,
and constraint satisfaction evidence, preventing hallucinated specifications.
"""

from typing import Any, Dict, List

def build_explainer_context(
    user_query: str,
    hard_constraints: Dict[str, Any],
    soft_intent: Dict[str, Any],
    pipeline_output: Dict[str, Any]
) -> str:
    """
    Serializes pipeline results into a structured, factual text context for the LLM.
    """
    lines = []
    lines.append("=== USER REQUEST ===")
    lines.append(f"Raw Query: \"{user_query}\"")
    lines.append("")

    lines.append("=== APPLIED HARD CONSTRAINTS (Deterministic ML Filtering) ===")
    lines.append(f"- In Stock Only: {hard_constraints.get('in_stock_only', True)}")
    if hard_constraints.get("gender"):
        lines.append(f"- Gender: {hard_constraints['gender']}")
    if hard_constraints.get("category"):
        lines.append(f"- Category: {hard_constraints['category']}")
    if hard_constraints.get("max_price"):
        lines.append(f"- Max Budget: Rs. {hard_constraints['max_price']}")
    if hard_constraints.get("excluded_patterns"):
        lines.append(f"- Excluded Patterns: {hard_constraints['excluded_patterns']}")
    if hard_constraints.get("excluded_materials"):
        lines.append(f"- Excluded Materials: {hard_constraints['excluded_materials']}")
    if hard_constraints.get("excluded_colors"):
        lines.append(f"- Excluded Colors: {hard_constraints['excluded_colors']}")
    
    retrieved = pipeline_output.get("retrieved_count", 0)
    filtered = pipeline_output.get("filtered_count", 0)
    rejected = pipeline_output.get("rejected_count", 0)
    lines.append(f"- Filtering Summary: {retrieved} candidates retrieved via FAISS, {rejected} rejected by constraints, {filtered} fully compliant survivors.")
    lines.append("")

    lines.append("=== TOP RANKED CANDIDATE PRODUCTS (Truth Grounding Data) ===")
    results: List[Dict[str, Any]] = pipeline_output.get("results", [])
    if not results:
        lines.append("No products survived hard constraint filtering.")
    else:
        for item in results:
            rank = item["rank"]
            pid = item["product_id"]
            title = item["title"]
            score = item["final_score"]
            details = item["product_details"]
            evidence = item["matched_evidence"]

            lines.append(f"Product #{rank}:")
            lines.append(f"  - Product ID: {pid}")
            lines.append(f"  - Title: {title}")
            lines.append(f"  - Brand: {details.get('brand', 'Unknown')}")
            lines.append(f"  - Price: Rs. {details.get('price')}")
            lines.append(f"  - Rating: {details.get('rating', 'N/A')} / 5.0")
            lines.append(f"  - Material: {details.get('material', 'N/A')}")
            lines.append(f"  - Pattern: {details.get('pattern', 'N/A')}")
            lines.append(f"  - Color: {details.get('dominant_color', 'N/A')}")
            lines.append(f"  - Match Score: {score:.1f} / 100")
            lines.append(f"  - Verified Evidence: {', '.join(evidence)}")
            lines.append("")

    return "\n".join(lines)
