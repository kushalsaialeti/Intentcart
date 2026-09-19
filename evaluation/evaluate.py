"""
IntentCart - ML Subsystem
Script: evaluation/evaluate.py
"""

import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from retrieval.vector_search import VectorSearchRetriever
from retrieval.filters import HardConstraintFilter
from retrieval.pipeline import IntentCartPipeline

def evaluate_systems():
    # 1. Load benchmark test queries
    eval_file = os.path.join(config.BASE_DIR, "evaluation", "test_queries.json")
    print(f"Loading evaluation benchmark from: {eval_file}...")
    with open(eval_file, "r", encoding="utf-8") as f:
        queries = json.load(f)
    print(f"Total benchmark queries: {len(queries)}\n")

    # 2. Initialize systems
    print("Initializing System A (Pure Vector Search) and System B (IntentCart Hybrid Engine)...")
    retriever = VectorSearchRetriever()
    pipeline = IntentCartPipeline(retriever=retriever)

    # Metrics accumulators
    metrics = {
        "system_a": {
            "total_returned": 0,
            "total_compliant": 0,
            "precisions": [],
            "reciprocal_ranks": [],
            "violations": {"price": 0, "stock": 0, "gender": 0, "pattern": 0, "category": 0}
        },
        "system_b": {
            "total_returned": 0,
            "total_compliant": 0,
            "precisions": [],
            "reciprocal_ranks": [],
            "violations": {"price": 0, "stock": 0, "gender": 0, "pattern": 0, "category": 0}
        }
    }

    print("Running evaluation across benchmark...")
    for q_item in queries:
        qid = q_item["id"]
        q_text = q_item["query"]
        hard_constraints = q_item.get("hard_constraints", {})
        soft_intent = q_item.get("soft_intent", {})

        # --- RUN SYSTEM A (Pure Semantic Vector Search) ---
        sys_a_raw = retriever.retrieve_candidates(q_text, top_k=5)
        sys_a_products = [prod for prod, _ in sys_a_raw]

        # Evaluate System A compliance
        a_compliant = 0
        a_first_rank = 0
        for rank, p in enumerate(sys_a_products, 1):
            is_valid, violations = HardConstraintFilter.evaluate_product(p, hard_constraints)
            if is_valid:
                a_compliant += 1
                if a_first_rank == 0:
                    a_first_rank = rank
            else:
                for v in violations:
                    v_low = v.lower()
                    if "price" in v_low: metrics["system_a"]["violations"]["price"] += 1
                    if "stock" in v_low: metrics["system_a"]["violations"]["stock"] += 1
                    if "gender" in v_low: metrics["system_a"]["violations"]["gender"] += 1
                    if "pattern" in v_low: metrics["system_a"]["violations"]["pattern"] += 1
                    if "category" in v_low: metrics["system_a"]["violations"]["category"] += 1

        n_a = max(1, len(sys_a_products))
        metrics["system_a"]["total_returned"] += len(sys_a_products)
        metrics["system_a"]["total_compliant"] += a_compliant
        metrics["system_a"]["precisions"].append(a_compliant / n_a)
        metrics["system_a"]["reciprocal_ranks"].append(1.0 / a_first_rank if a_first_rank > 0 else 0.0)

        # --- RUN SYSTEM B (IntentCart Hybrid Engine) ---
        sys_b_res = pipeline.run(q_text, hard_constraints=hard_constraints, soft_intent=soft_intent, top_k=5)
        # Extract product details from pipeline results
        sys_b_products = []
        for r in sys_b_res["results"]:
            prod = dict(r["product_details"])
            prod["id"] = r["product_id"]
            prod["title"] = r["title"]
            sys_b_products.append(prod)

        # Evaluate System B compliance
        b_compliant = 0
        b_first_rank = 0
        for rank, p in enumerate(sys_b_products, 1):
            is_valid, violations = HardConstraintFilter.evaluate_product(p, hard_constraints)
            if is_valid:
                b_compliant += 1
                if b_first_rank == 0:
                    b_first_rank = rank
            else:
                for v in violations:
                    v_low = v.lower()
                    if "price" in v_low: metrics["system_b"]["violations"]["price"] += 1
                    if "stock" in v_low: metrics["system_b"]["violations"]["stock"] += 1
                    if "gender" in v_low: metrics["system_b"]["violations"]["gender"] += 1
                    if "pattern" in v_low: metrics["system_b"]["violations"]["pattern"] += 1
                    if "category" in v_low: metrics["system_b"]["violations"]["category"] += 1

        n_b = max(1, len(sys_b_products))
        metrics["system_b"]["total_returned"] += len(sys_b_products)
        metrics["system_b"]["total_compliant"] += b_compliant
        metrics["system_b"]["precisions"].append(b_compliant / n_b)
        metrics["system_b"]["reciprocal_ranks"].append(1.0 / b_first_rank if b_first_rank > 0 else 0.0)

    # 3. Calculate aggregate summary
    csr_a = (metrics["system_a"]["total_compliant"] / max(1, metrics["system_a"]["total_returned"])) * 100
    csr_b = (metrics["system_b"]["total_compliant"] / max(1, metrics["system_b"]["total_returned"])) * 100

    p_a = np.mean(metrics["system_a"]["precisions"]) * 100
    p_b = np.mean(metrics["system_b"]["precisions"]) * 100

    mrr_a = np.mean(metrics["system_a"]["reciprocal_ranks"])
    mrr_b = np.mean(metrics["system_b"]["reciprocal_ranks"])

    # 4. Print A/B Comparison Report
    print("\n" + "=" * 85)
    print("           INTENTCART OFFLINE EVALUATION & A/B EXPERIMENT REPORT")
    print("=" * 85)
    print(f"Benchmark Size: {len(queries)} queries across 10 categories (Wedding, Summer, Budget, etc.)")
    print("-" * 85)
    print(f"{'Evaluation Metric':<32} {'System A (Pure Vector)':<25} {'System B (IntentCart)':<25}")
    print("-" * 85)
    print(f"{'Constraint Satisfaction (CSR@5)':<32} {csr_a:>6.2f}%{'':<18} {csr_b:>6.2f}%")
    print(f"{'Mean Precision@5':<32} {p_a:>6.2f}%{'':<18} {p_b:>6.2f}%")
    print(f"{'Mean Reciprocal Rank (MRR)':<32} {mrr_a:>6.4f}{'':<19} {mrr_b:>6.4f}")
    print(f"{'Total Returned Products':<32} {metrics['system_a']['total_returned']:>6}{'':<19} {metrics['system_b']['total_returned']:>6}")
    print(f"{'Fully Compliant Products':<32} {metrics['system_a']['total_compliant']:>6}{'':<19} {metrics['system_b']['total_compliant']:>6}")
    print("-" * 85)

    print("\n--- Breakdown of Hard Constraint Violations Detected ---")
    print(f"{'Violation Category':<32} {'System A (Pure Vector)':<25} {'System B (IntentCart)':<25}")
    print("-" * 85)
    for cat in ["stock", "gender", "category", "price", "pattern"]:
        v_a = metrics["system_a"]["violations"][cat]
        v_b = metrics["system_b"]["violations"][cat]
        print(f"{cat.capitalize() + ' Violations':<32} {v_a:>6}{'':<19} {v_b:>6}")
    print("=" * 85)

    print("\n--- Metric Definitions ---")
    print("1. CSR@5 (Constraint Satisfaction Rate):")
    print("   Total products satisfying 100% of user hard constraints divided by total products returned.")
    print("2. Precision@5:")
    print("   Average proportion of top-5 recommended products per query that satisfy all user requirements.")
    print("3. MRR (Mean Reciprocal Rank):")
    print("   Evaluates how early in the rank list the FIRST valid product appears (1/rank). A score of 1.0 means")
    print("   the #1 ranked product is always compliant.")

    assert csr_b > csr_a, "IntentCart CSR must exceed pure vector baseline!"
    assert p_b > p_a, "IntentCart Precision must exceed pure vector baseline!"

if __name__ == "__main__":
    evaluate_systems()
