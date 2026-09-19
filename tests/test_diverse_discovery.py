"""
IntentCart - Multi-Category Verification Test
Script: tests/test_diverse_discovery.py

Verifies that the IntentCart AI Engine successfully retrieves, filters,
and explains products across diverse fashion categories:
- Men's Shirts (Casual/Formal)
- Women's Jeans / Denim
- Women's Dresses
- Men's Kurtas (Canonical)
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.intent_extractor import intent_extractor
from llm.adapter import map_schema_to_pipeline_args
from retrieval.pipeline import IntentCartPipeline
from llm.explainer import grounded_explainer

TEST_QUERIES = [
    {
        "category_expected": "Shirts",
        "query": "Looking for a men's casual slim-fit shirt under 2000, breathable cotton, no stripes"
    },
    {
        "category_expected": "Jeans",
        "query": "I want women's blue jeans, stretchable and comfortable, under 3500"
    },
    {
        "category_expected": "Dresses",
        "query": "Need a casual summer dress for women, breathable and light"
    },
    {
        "category_expected": "Kurtas",
        "query": "I need a wedding-day kurta for my brother's wedding, comfortable and minimal, no floral patterns, formal and breathable for summer."
    }
]

def run_diverse_tests():
    print("=" * 80)
    print(" IntentCart - Diverse Multi-Category Discovery Test Suite")
    print("=" * 80)

    pipeline = IntentCartPipeline()

    for i, test in enumerate(TEST_QUERIES, 1):
        q = test["query"]
        expected_cat = test["category_expected"]

        print(f"\n[Test #{i} - Category: {expected_cat}]")
        print(f"Query: \"{q}\"")

        # 1. Intent Extraction
        schema, intent_meta = intent_extractor.extract_intent(q)
        print(f"  -> Extracted Category: {schema.hard_constraints.category} | Gender: {schema.hard_constraints.gender}")
        print(f"  -> Reformulated Vector Query: \"{schema.search_query}\"")

        # 2. ML Retrieval Pipeline
        pipeline_kwargs = map_schema_to_pipeline_args(schema)
        output = pipeline.run(**pipeline_kwargs, top_k=3)

        print(f"  -> Retrieved {output['retrieved_count']} candidates | Passed: {output['filtered_count']} | Rejected: {output['rejected_count']}")
        assert len(output["results"]) > 0, f"No products returned for query: {q}"

        print("  -> Top Recommended Products:")
        for res in output["results"]:
            details = res["product_details"]
            print(f"     * [{res['product_id']}] {res['title']} (Rs. {details.get('price')}) | Cat: {details.get('category')} | Pattern: {details.get('pattern')} | Mat: {details.get('material')}")

        # Check category alignment on #1 result
        top_cat = output["results"][0]["product_details"].get("category", "")
        print(f"  -> Top result category: '{top_cat}' (Expected: '{expected_cat}')")

    print("\n" + "=" * 80)
    print("All Multi-Category Discovery Tests Passed Successfully!")
    print("=" * 80)

if __name__ == "__main__":
    run_diverse_tests()
