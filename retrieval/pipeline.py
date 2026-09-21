"""
IntentCart - ML Subsystem
Module: retrieval/pipeline.py

Objective:
End-to-end IntentCart Retrieval and Ranking Pipeline.
Orchestrates:
1. Controlled vector candidate retrieval (FAISS IndexFlatIP, pool size 100-150)
2. Step-by-step deterministic filtering:
   - Exact canonical category verification (Eligibility)
   - Gender compatibility (Only when explicitly specified)
   - Budget constraints (Max/Min price)
   - Stock availability (In-stock only)
   - Negative constraints (Forbidden patterns, colors, materials)
3. Soft preference & semantic hybrid scoring
4. Selection and ranking of Top 3-5 best products (No category backfilling)
5. Full debug/trace telemetry and rejection logging
"""

import os
import sys
from typing import Any, Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from retrieval.vector_search import VectorSearchRetriever
from retrieval.filters import HardConstraintFilter
from retrieval.category_normalizer import normalize_to_canonical_category
from ranking.scorer import HybridScorer

class IntentCartPipeline:
    """
    Unified ML Retrieval and Ranking Engine.
    Executes the multi-stage discovery workflow.
    """

    def __init__(
        self,
        retriever: VectorSearchRetriever = None,
        scorer: HybridScorer = None,
        retrieval_k: int = 120,
        final_k: int = config.FINAL_K
    ):
        self.retriever = retriever or VectorSearchRetriever()
        self.scorer = scorer or HybridScorer()
        self.retrieval_k = max(retrieval_k, 120)
        self.final_k = final_k

    def run(
        self,
        query: str,
        hard_constraints: dict[str, Any] = None,
        soft_intent: dict[str, Any] = None,
        top_k: int = None
    ) -> dict[str, Any]:
        """
        Executes complete discovery flow for a query.
        
        Args:
            query: Natural language or dense reformulated query string.
            hard_constraints: Dict of deterministic rules:
                - max_price, min_price, gender, gender_specified, category,
                  canonical_category, in_stock_only, excluded_patterns, excluded_materials,
                  excluded_colors, negative_constraints
            soft_intent: Dict of soft preferences:
                - preferences: list of keywords (e.g. ['minimal', 'breathable', 'comfortable'])
                - occasion: target occasion (e.g. 'wedding')
                - season: target season (e.g. 'summer')
            top_k: Number of final ranked products to return (default FINAL_K=5).
        """
        target_final_k = top_k or self.final_k
        hard_constraints = hard_constraints or {}
        soft_intent = soft_intent or {}

        # 1. Vector Search: Retrieve a deep candidate pool (120 items)
        pool_size = max(self.retrieval_k, 120)
        raw_candidates = self.retriever.retrieve_candidates(query, top_k=pool_size)
        initial_count = len(raw_candidates)

        sim_lookup = {prod["id"]: sim for prod, sim in raw_candidates}
        current_candidates = [prod for prod, _ in raw_candidates]

        # 2. Multi-Stage Deterministic Filtering Funnel for Debug Trace
        rejections = []

        # Stage A: Canonical Category Filter
        req_cat = hard_constraints.get("canonical_category") or hard_constraints.get("category")
        category_passed = []
        if req_cat:
            canonical_target = normalize_to_canonical_category(req_cat)
            cat_constraint = {"canonical_category": canonical_target}
            category_passed, cat_rejected = HardConstraintFilter.apply_hard_constraints(
                current_candidates, cat_constraint
            )
            rejections.extend(cat_rejected)
        else:
            category_passed = list(current_candidates)
        category_count = len(category_passed)

        # Stage B: Hard Constraints (Budget, Stock, Gender)
        hard_subset = {
            "gender": hard_constraints.get("gender"),
            "gender_specified": hard_constraints.get("gender_specified"),
            "max_price": hard_constraints.get("max_price"),
            "min_price": hard_constraints.get("min_price"),
            "in_stock_only": hard_constraints.get("in_stock_only", True)
        }
        hard_passed, hard_rejected = HardConstraintFilter.apply_hard_constraints(
            category_passed, hard_subset
        )
        rejections.extend(hard_rejected)
        hard_count = len(hard_passed)

        # Stage C: Negative Constraints (Excluded patterns, materials, colors)
        neg_subset = {
            "excluded_patterns": hard_constraints.get("excluded_patterns", []),
            "excluded_materials": hard_constraints.get("excluded_materials", []),
            "excluded_colors": hard_constraints.get("excluded_colors", []),
            "negative_constraints": hard_constraints.get("negative_constraints", [])
        }
        surviving_products, neg_rejected = HardConstraintFilter.apply_hard_constraints(
            hard_passed, neg_subset
        )
        rejections.extend(neg_rejected)
        negative_count = len(surviving_products)

        # 3. Determine Match Status
        if surviving_products:
            match_status = "exact"
        else:
            match_status = "no_exact_match"

        # 4. Hybrid Scoring & Ranking of Surviving Candidates ONLY
        surviving_candidate_pairs = [
            (prod, sim_lookup.get(prod["id"], 0.5)) for prod in surviving_products
        ]

        if surviving_candidate_pairs:
            ranked_products = self.scorer.rank_candidates(
                surviving_candidate_pairs, soft_intent, top_k=target_final_k
            )
        else:
            ranked_products = []

        return {
            "query": query,
            "match_status": match_status,
            "requested_category": req_cat,
            "retrieved_count": initial_count,
            "filtered_count": len(surviving_products),
            "rejected_count": len(rejections),
            "final_count": len(ranked_products),
            "results": ranked_products,
            "trace": {
                "initial_candidate_count": initial_count,
                "candidate_pool_size": initial_count,
                "category_filtered_count": category_count,
                "after_category_filter": category_count,
                "hard_constraint_valid_count": hard_count,
                "after_hard_filter": hard_count,
                "negative_constraint_valid_count": negative_count,
                "after_negative_filter": negative_count,
                "final_candidate_count": len(ranked_products),
                "rejection_counts": len(rejections),
                "rejections": rejections
            }
        }
