"""
IntentCart - Master AI Discovery CLI
Script: run_intentcart_ai.py

Objective (Phase L12):
Interactive and CLI execution of the full IntentCart AI Discovery Engine:
1. Multi-model racing LLM extracts structured hard and soft constraints
2. Deterministic ML pipeline performs FAISS retrieval, hard filtering, and hybrid ranking
3. Grounded Explainer generates conversational stylist recommendations
"""

import sys
import os
import json
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from llm.intent_extractor import intent_extractor
from llm.adapter import map_schema_to_pipeline_args
from retrieval.pipeline import IntentCartPipeline
from llm.explainer import grounded_explainer
import llm.config as config

def run_discovery_session(user_query: str, top_k: int = 5):
    print("=" * 80)
    print(" INTENTCART AI -- CONSTRAINT-AWARE PRODUCT DISCOVERY ENGINE")
    print("=" * 80)
    print(f"\nUser Query:\n  \"{user_query}\"\n")

    t0 = time.perf_counter()

    # 1. Multi-Model Racing Intent Extraction
    print("[1/3] Deconstructing natural language intent via Multi-Model Racing...")
    schema, intent_meta = intent_extractor.extract_intent(user_query)
    intent_time = round((time.perf_counter() - t0) * 1000, 2)

    winner_prov = intent_meta.get("provider", "").upper()
    winner_mod = intent_meta.get("model", "")
    print(f"      -> Intent Winner: {winner_prov} ({winner_mod}) in {intent_meta.get('latency_ms')} ms")
    
    # Show extracted constraints
    hard_dict = schema.hard_constraints.model_dump(exclude_none=True)
    soft_dict = {k: v for k, v in schema.soft_preferences.model_dump().items() if v not in (0.5, None, [])}
    print(f"      -> Enforced Hard Constraints: {hard_dict}")
    print(f"      -> Positive Soft Preferences: {soft_dict}")
    print(f"      -> Reformulated Search Query : \"{schema.search_query}\"")

    # 2. Deterministic ML Retrieval Pipeline
    print("\n[2/3] Executing Deterministic ML Pipeline (Untouched FAISS + Filters + Scorer)...")
    pipeline_kwargs = map_schema_to_pipeline_args(schema)
    pipeline = IntentCartPipeline()
    ml_output = pipeline.run(**pipeline_kwargs, top_k=top_k)

    """
    print(f"      -> Dense Candidates Retrieved: {ml_output['retrieved_count']}")
    print(f"      -> Hard Constraint Passed    : {ml_output['filtered_count']}")
    print(f"      -> Hard Constraint Rejected  : {ml_output['rejected_count']}")
"""
    if ml_output['rejected_count'] > 0 and ml_output.get('rejections'):
        sample_rej = ml_output['rejections'][0]
        # print(f"      -> Sample Rejection Reason   : [{sample_rej['product_id']}] {sample_rej['reasons']}")

    # 3. Grounded Conversational Explanation
    print("\n[3/3] Generating Grounded Stylist Recommendations via LLMRouter...")
    explanation, explainer_meta = grounded_explainer.explain_recommendations(
        user_query=user_query,
        hard_constraints=pipeline_kwargs["hard_constraints"],
        soft_intent=pipeline_kwargs["soft_intent"],
        pipeline_output=ml_output
    )
    total_time = round((time.perf_counter() - t0) * 1000, 2)

    print(f"      -> Explainer Winner: {explainer_meta.get('provider', '').upper()} ({explainer_meta.get('model', '')}) in {explainer_meta.get('latency_ms')} ms")

    print("\n" + "=" * 80)
    print(" CONVERSATIONAL STYLIST RECOMMENDATIONS")
    print("=" * 80)
    print(explanation)
    print("-" * 80)
    print(f"End-to-End Discovery Pipeline Latency: {total_time} ms")
    print("=" * 80)

    return {
        "query": user_query,
        "schema": schema.model_dump(),
        "ml_output": ml_output,
        "explanation": explanation,
        "total_latency_ms": total_time
    }

def interactive_loop():
    print("IntentCart AI Interactive Mode. Type your query or 'exit' to quit.\n")
    while True:
        try:
            query = input("\nEnter shopping request: ").strip()
            if not query or query.lower() in ("exit", "quit", "q"):
                break
            run_discovery_session(query)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    canonical_query = (
        "I need a wedding-day kurta for my brother's wedding, "
        "comfortable and minimal, no floral patterns, "
        "formal and breathable for summer."
    )

    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_loop()
        else:
            user_input = " ".join(sys.argv[1:])
            run_discovery_session(user_input)
    else:
        run_discovery_session(canonical_query)
