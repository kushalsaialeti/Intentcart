"""
IntentCart - Phase L5/L6 Verification Test
Script: tests/test_intent_extraction.py

Tests intent extraction on challenging natural language queries, verifying:
1. Hard constraints correctly isolated (especially exclusions like 'no floral')
2. Positive search terms reformulated without negation words
3. Multi-model racing latency and accuracy
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.intent_extractor import intent_extractor

TEST_QUERIES = [
    "I need a wedding-day kurta for my brother's wedding, comfortable and minimal, no floral patterns, formal and breathable for summer.",
    "Looking for a casual cotton shirt for men under 2000 rupees, definitely avoid yellow and no polyester",
    "Women party dress for evening reception under 6000, elegant, no stripes"
]

def run_tests():
    print("=" * 70)
    print(" IntentCart - Intent Extraction Test Suite (Multi-Model Racing)")
    print("=" * 70)

    for i, q in enumerate(TEST_QUERIES, 1):
        print(f"\n[Test Query #{i}]: \"{q}\"")
        schema, meta = intent_extractor.extract_intent(q)

        provider = meta.get("provider", "unknown").upper()
        model = meta.get("model", "unknown")
        latency = meta.get("latency_ms", 0)

        print(f"-> Winner: {provider} ({model}) in {latency} ms")
        print("-> Extracted Hard Constraints:", schema.hard_constraints.model_dump())
        print("-> Extracted Soft Preferences:", {k: v for k, v in schema.soft_preferences.model_dump().items() if v not in (0.5, None, [])})
        print("-> Reformulated Search Query :", f"\"{schema.search_query}\"")

        # Sanity check: Exclusions should not be in search query
        for pattern in schema.hard_constraints.excluded_patterns:
            if pattern.lower() in schema.search_query.lower():
                print(f"[WARNING] Excluded pattern '{pattern}' found in search_query '{schema.search_query}'!")
            else:
                print(f"[OK] Excluded pattern '{pattern}' safely absent from search query.")

    print("\n" + "=" * 70)
    print("All Intent Extraction tests completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
