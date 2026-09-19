"""
IntentCart - ML Subsystem
Script: run_ml_pipeline.py
"""

import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from retrieval.pipeline import IntentCartPipeline

def parse_query_intent_rule_based(query: str) -> tuple[dict, dict]:
    """
    Deterministic rule-based intent parser for ML prototype stage
    (used before LLM integration).
    Extracts hard constraints and soft preferences directly from natural text.
    """
    q_lower = query.lower()
    hard_constraints = {"in_stock_only": True}
    soft_intent = {"preferences": []}

    # 1. Price / Budget extraction (e.g. 'under 5000', 'under ₹5,000', 'below 4000')
    price_match = re.search(r"(?:under|below|less than|within|upto|budget of)\s*(?:rs\.?|inr|₹)?\s*(\d+[\d,]*)", q_lower)
    if price_match:
        budget_str = price_match.group(1).replace(",", "")
        hard_constraints["max_price"] = int(budget_str)

    # 2. Pattern exclusions (e.g. 'no floral', 'without floral', 'avoid prints')
    excluded = []
    if "no floral" in q_lower or "without floral" in q_lower or "not floral" in q_lower:
        excluded.append("floral")
    if "no print" in q_lower or "without print" in q_lower:
        excluded.append("printed")
    if excluded:
        hard_constraints["excluded_patterns"] = excluded

    # 3. Gender extraction
    if any(w in q_lower for w in ["men", "brother", "father", "husband", "groom", "boy", "guy"]):
        hard_constraints["gender"] = "Men"
    elif any(w in q_lower for w in ["women", "sister", "mother", "wife", "bride", "girl", "lady"]):
        hard_constraints["gender"] = "Women"

    # 4. Category extraction
    if "kurta" in q_lower or "kurti" in q_lower:
        hard_constraints["category"] = "Kurta"
    elif "shirt" in q_lower:
        hard_constraints["category"] = "Shirt"
    elif "dress" in q_lower or "gown" in q_lower or "anarkali" in q_lower:
        hard_constraints["category"] = "Dress"

    # 5. Soft preferences extraction
    for word in ["minimal", "breathable", "comfortable", "lightweight", "simple", "elegant", "classic"]:
        if word in q_lower:
            soft_intent["preferences"].append(word)

    # 6. Occasion extraction
    if "wedding" in q_lower or "reception" in q_lower or "marriage" in q_lower:
        soft_intent["occasion"] = "wedding"
    elif "formal" in q_lower or "office" in q_lower or "meeting" in q_lower:
        soft_intent["occasion"] = "formal"
    elif "casual" in q_lower or "daily" in q_lower:
        soft_intent["occasion"] = "casual"

    # 7. Season / Climate extraction
    if "summer" in q_lower or "hot" in q_lower or "warm" in q_lower or "breathable" in q_lower:
        soft_intent["season"] = "summer"
    elif "winter" in q_lower or "cold" in q_lower:
        soft_intent["season"] = "winter"

    return hard_constraints, soft_intent

def display_pipeline_results(result: dict):
    """Renders formatted results matching Section 40 specification."""
    query = result["query"]
    retrieved = result["retrieved_count"]
    filtered = result["filtered_count"]
    rejected = result["rejected_count"]
    results = result["results"]

    print("\n" + "=" * 80)
    print("           INTENTCART ML RETRIEVAL & RANKING RESULTS")
    print("=" * 80)
    print(f"User Query: \"{query}\"")
    print(f"Candidates retrieved from FAISS: {retrieved}")
    print(f"Candidates after hard filtering: {filtered} (Rejected: {rejected})\n")

    if not results:
        print("No products matched the combined hard constraints and query intent.")
        return

    for item in results:
        rank = item["rank"]
        pid = item["product_id"]
        title = item["title"]
        score = item["final_score"]
        bd = item["score_breakdown"]
        details = item["product_details"]
        evidence = item["matched_evidence"]

        print(f"#{rank} Product [{pid}]")
        print(f"Title: {title}")
        print(f"Final Score: {score:.2f} / 100")
        print(f"  Price: Rs.{details['price']} | Gender: {details['gender']} | Pattern: {details['pattern']} | Material: {details['material']}")
        print(f"  Score Breakdown:")
        print(f"    - Semantic Similarity (50%):  {bd['semantic']:.4f}  (Score: {bd['semantic']*50:.1f})")
        print(f"    - Soft Preference Match (20%): {bd['preference']:.4f}  (Score: {bd['preference']*20:.1f})")
        print(f"    - Occasion Match (15%):        {bd['occasion']:.4f}  (Score: {bd['occasion']*15:.1f})")
        print(f"    - Season Match (10%):          {bd['season']:.4f}  (Score: {bd['season']*10:.1f})")
        print(f"    - Customer Rating (5%):        {bd['rating']:.4f}  (Score: {bd['rating']*5:.1f})")
        
        print("  Matched Evidence:")
        for ev in evidence:
            print(f"    [OK] {ev}")
        print("-" * 80)

def main():
    pipeline = IntentCartPipeline()

    # The canonical test query from Section 2 and Section 40:
    canonical_query = (
        "I need a wedding-day kurta for my brother's wedding, "
        "comfortable and minimal, no floral patterns, "
        "formal and breathable for summer."
    )

    # Check if a custom query was passed via command line argument
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = canonical_query

    print(f"\nProcessing Discovery Query:\n  \"{user_query}\"")
    
    # 1. Parse intent
    hard_constraints, soft_intent = parse_query_intent_rule_based(user_query)
    print("\nExtracted Intent:")
    print(f"  Hard Constraints: {hard_constraints}")
    print(f"  Soft Preferences: {soft_intent}")

    # 2. Run retrieval pipeline
    result = pipeline.run(
        query=user_query,
        hard_constraints=hard_constraints,
        soft_intent=soft_intent,
        top_k=5
    )

    # 3. Display structured output
    display_pipeline_results(result)

if __name__ == "__main__":
    main()
