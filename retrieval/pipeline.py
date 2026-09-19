"""
IntentCart - ML Subsystem
Module: retrieval/pipeline.py

Objective (Phases 17, 18, 19):
End-to-end IntentCart Retrieval and Ranking Pipeline.
Orchestrates:
1. Vector candidate retrieval (FAISS IndexFlatIP, Top 20-50)
2. Deterministic hard-constraint filtering (budget, stock, gender, pattern exclusions)
3. Soft preference & semantic hybrid scoring
4. Selection and ranking of Top 3-5 best products
5. Generation of score breakdowns and grounded explanation evidence
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from retrieval.vector_search import VectorSearchRetriever
from retrieval.filters import HardConstraintFilter
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
        retrieval_k: int = config.RETRIEVAL_K,
        final_k: int = config.FINAL_K
    ):
        self.retriever = retriever or VectorSearchRetriever()
        self.scorer = scorer or HybridScorer()
        self.retrieval_k = retrieval_k
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
            query: Natural language user query string.
            hard_constraints: Dict of deterministic rules:
                - max_price, min_price, gender, category, in_stock_only, excluded_patterns
            soft_intent: Dict of soft preferences:
                - preferences: list of keywords (e.g. ['minimal', 'breathable', 'comfortable'])
                - occasion: target occasion (e.g. 'wedding')
                - season: target season (e.g. 'summer')
            top_k: Number of final ranked products to return (default FINAL_K=5).
        """
        target_final_k = top_k or self.final_k
        hard_constraints = hard_constraints or {}
        soft_intent = soft_intent or {}

        # 1. Vector Search: Retrieve Top-K semantic candidates
        # We retrieve max(retrieval_k, 50) to allow a healthy buffer for hard filtering
        pool_size = max(self.retrieval_k, 50)
        raw_candidates = self.retriever.retrieve_candidates(query, top_k=pool_size)
        retrieved_count = len(raw_candidates)

        # 2. Hard Constraint Filtering
        candidate_products = [prod for prod, _ in raw_candidates]
        sim_lookup = {prod["id"]: sim for prod, sim in raw_candidates}

        passed_products, rejected_records = HardConstraintFilter.apply_hard_constraints(
            candidate_products, hard_constraints
        )
        filtered_count = len(passed_products)

        # Re-attach similarity scores for passed candidates
        surviving_candidates = [
            (prod, sim_lookup[prod["id"]]) for prod in passed_products
        ]

        # 3. Hybrid Scoring & Ranking
        ranked_products = self.scorer.rank_candidates(
            surviving_candidates, soft_intent, top_k=target_final_k
        )

        return {
            "query": query,
            "retrieved_count": retrieved_count,
            "filtered_count": filtered_count,
            "rejected_count": len(rejected_records),
            "results": ranked_products,
            "rejections": rejected_records[:5]  # Sample of top rejected items for inspection
        }
