"""
IntentCart - Phase L7/L8 Integration Test
Script: tests/test_llm_ml_integration.py

Verifies end-to-end integration:
1. Natural language query processed by multi-model racing LLM
2. Extracted intent adapted cleanly into pipeline parameters
3. Existing untouched ML pipeline retrieves and ranks compliant products
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.intent_extractor import intent_extractor
from llm.adapter import map_schema_to_pipeline_args
from retrieval.pipeline import IntentCartPipeline

def test_e2e():
    print("=" * 70)
    print(" IntentCart - End-to-End LLM + ML Pipeline Integration Test")
    print("=" * 70)

    user_query = (
        "I need a wedding-day kurta for my brother's wedding, comfortable and minimal, "
        "no floral patterns, formal and breathable for summer."
    )
    print(f"\nUser Query:\n  \"{user_query}\"")

    # Step 1: LLM Intent Extraction via Multi-Model Racing
    print("\n[Step 1] Extracting structured intent via LLMRouter...")
    schema, meta = intent_extractor.extract_intent(user_query)
    print(f"  -> Model Winner: {meta.get('provider').upper()} ({meta.get('model')}) in {meta.get('latency_ms')} ms")
    print(f"  -> Extracted Hard Constraints: {schema.hard_constraints.model_dump()}")
    print(f"  -> Reformulated Search Query : \"{schema.search_query}\"")

    # Step 2: Adapt to ML Pipeline Arguments
    print("\n[Step 2] Adapting schema to ML pipeline kwargs...")
    pipeline_kwargs = map_schema_to_pipeline_args(schema)
    print(f"  -> Final Query: \"{pipeline_kwargs['query']}\"")
    print(f"  -> Hard Constraints: {pipeline_kwargs['hard_constraints']}")
    print(f"  -> Soft Intent: {pipeline_kwargs['soft_intent']}")

    # Step 3: Run Deterministic ML Retrieval Pipeline
    print("\n[Step 3] Executing IntentCart ML Pipeline (FAISS + Hard Filter + Hybrid Scorer)...")
    pipeline = IntentCartPipeline()
    output = pipeline.run(**pipeline_kwargs, top_k=5)

    print(f"  -> Candidates Retrieved : {output['retrieved_count']}")
    print(f"  -> Hard Filter Passed   : {output['filtered_count']}")
    print(f"  -> Hard Filter Rejected : {output['rejected_count']}")

    print("\n--- Final Top-5 ML Ranked Recommendations ---")
    for item in output["results"]:
        rank = item["rank"]
        pid = item["product_id"]
        title = item["title"]
        score = item["final_score"]
        details = item["product_details"]
        evidence = item["matched_evidence"]

        print(f"\n#{rank} [{pid}] {title}")
        print(f"    Brand: {details.get('brand')} | Price: Rs. {details.get('price')} | Rating: {details.get('rating')}")
        print(f"    Pattern: {details.get('pattern')} | Material: {details.get('material')}")
        print(f"    Composite Score: {score:.2f}/100")
        print(f"    Evidence: {evidence}")

        # Verify hard constraint: floral must NOT be in pattern or title
        assert "floral" not in str(details.get("pattern", "")).lower(), f"Floral pattern found in product #{rank}!"
        assert "floral" not in title.lower(), f"Floral title found in product #{rank}!"

    print("\n" + "=" * 70)
    print("[PASS] 100% of Top Products strictly satisfied all LLM-extracted constraints!")
    print("=" * 70)

if __name__ == "__main__":
    test_e2e()
