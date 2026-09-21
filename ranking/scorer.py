"""
IntentCart - ML Subsystem
Module: ranking/scorer.py

Objective:
Hybrid Scorer and Candidate Ranker.
Combines semantic similarity and soft preference dimensions into an explainable,
weighted score (0 to 100) using configurable weights from config.py.
"""

import sys
import os
from typing import Any, List, Dict, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from retrieval.preference_matcher import PreferenceMatcher

class HybridScorer:
    """
    Computes transparent multi-criteria relevance scores for candidates.
    Weights are centralized in config.SCORING_WEIGHTS.
    """

    def __init__(self, weights: dict[str, float] = None):
        self.weights = weights or config.SCORING_WEIGHTS

    def score_candidate(
        self,
        product: dict,
        semantic_similarity: float,
        soft_intent: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Calculates subscores and final weighted composite score for a product.
        
        Args:
            product: Product metadata dict
            semantic_similarity: Cosine similarity from FAISS (0.0 to 1.0)
            soft_intent: Dict containing:
                - preferences: list of soft preferences (e.g. ['minimal', 'breathable', 'comfortable'])
                - occasion: target occasion string (e.g. 'wedding')
                - season: target season string (e.g. 'summer')
        """
        preferences = soft_intent.get("preferences", [])
        target_occasion = soft_intent.get("occasion", "")
        target_season = soft_intent.get("season", "")

        # 1. Semantic score (bounded 0.0 to 1.0)
        s_semantic = max(0.0, min(1.0, float(semantic_similarity)))

        # 2. Preference match score & evidence
        s_pref, pref_evidence = PreferenceMatcher.score_comfort_and_preferences(product, preferences)

        # 3. Occasion suitability score & evidence
        s_occ, occ_evidence = PreferenceMatcher.score_occasion(product, target_occasion)

        # 4. Season / Climate suitability score & evidence
        s_season, season_evidence = PreferenceMatcher.score_season(product, target_season)

        # 5. Rating score
        s_rating = PreferenceMatcher.score_rating(product)

        # Weighted calculation (Scale to 0-100)
        weighted_sum = (
            self.weights["semantic"] * s_semantic +
            self.weights["preference"] * s_pref +
            self.weights["occasion"] * s_occ +
            self.weights["season"] * s_season +
            self.weights["rating"] * s_rating
        )
        final_score = round(weighted_sum * 100, 2)

        matched_evidence = []
        matched_evidence.extend(pref_evidence)
        matched_evidence.extend(occ_evidence)
        matched_evidence.extend(season_evidence)

        # Unmatched preference determination
        unmatched_preferences = []
        for p in preferences:
            p_lower = p.lower()
            if not any(p_lower in ev.lower() for ev in matched_evidence):
                unmatched_preferences.append(p)

        return {
            "product_id": product.get("id"),
            "title": product.get("title"),
            "final_score": final_score,
            "score_breakdown": {
                "semantic": round(s_semantic, 4),
                "preference": round(s_pref, 4),
                "occasion": round(s_occ, 4),
                "season": round(s_season, 4),
                "rating": round(s_rating, 4)
            },
            "matched_evidence": matched_evidence,
            "unmatched_preferences": unmatched_preferences,
            "product_details": {
                "price": product.get("price"),
                "category": product.get("category"),
                "gender": product.get("gender"),
                "material": product.get("material"),
                "pattern": product.get("pattern"),
                "color": product.get("color"),
                "in_stock": product.get("in_stock", product.get("stock", 0) > 0)
            }
        }

    def rank_candidates(
        self,
        candidates: list[tuple[dict, float]],
        soft_intent: dict[str, Any],
        top_k: int = config.FINAL_K
    ) -> list[dict[str, Any]]:
        """
        Scores and ranks surviving candidates in descending order of final_score.
        
        Args:
            candidates: List of (product_dict, cosine_similarity_score)
            soft_intent: Dict with soft preferences, occasion, season
            top_k: Number of top results to return (default FINAL_K=5)
        """
        scored_results = []
        for product, sim in candidates:
            scored = self.score_candidate(product, sim, soft_intent)
            scored_results.append(scored)

        # Sort strictly descending by final composite score
        scored_results.sort(key=lambda x: x["final_score"], reverse=True)

        # Attach 1-based rank
        for rank_num, item in enumerate(scored_results, 1):
            item["rank"] = rank_num

        return scored_results[:top_k]
