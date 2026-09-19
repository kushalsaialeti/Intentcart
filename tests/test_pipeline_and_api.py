"""
IntentCart - ML Subsystem
Test Suite: tests/test_pipeline_and_api.py
"""

import os
import sys
import unittest
import numpy as np
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from embeddings.model_loader import get_embedding_model
from retrieval.filters import HardConstraintFilter
from retrieval.vector_search import VectorSearchRetriever
from ranking.scorer import HybridScorer
from retrieval.pipeline import IntentCartPipeline
from api.main import app

class TestIntentCartMLSubsystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = get_embedding_model()
        cls.retriever = VectorSearchRetriever()
        cls.scorer = HybridScorer()
        cls.pipeline = IntentCartPipeline(retriever=cls.retriever, scorer=cls.scorer)
        cls.client = TestClient(app)

    # 1. Test Embedding Generation
    def test_embedding_generation(self):
        text = "sample summer wedding kurta"
        emb = self.model.encode([text], normalize_embeddings=True, convert_to_numpy=True)
        self.assertIsInstance(emb, np.ndarray)
        self.assertEqual(emb.shape[0], 1)

    # 2. Test Vector Dimensions
    def test_vector_dimensions(self):
        text = "sample text"
        emb = self.model.encode(text)
        self.assertEqual(len(emb), config.EMBEDDING_DIMENSION)
        self.assertEqual(len(emb), 384)

    # 3. Test FAISS Search
    def test_faiss_search(self):
        candidates = self.retriever.retrieve_candidates("cotton kurta", top_k=5)
        self.assertEqual(len(candidates), 5)
        # Cosine similarity must be between 0.0 and 1.0
        self.assertGreaterEqual(candidates[0][1], 0.0)
        self.assertLessEqual(candidates[0][1], 1.0)
        # Candidates must be in descending order of similarity
        for i in range(len(candidates) - 1):
            self.assertGreaterEqual(candidates[i][1], candidates[i+1][1])

    # 4. Test Price Filter
    def test_price_filter(self):
        dummy_products = [
            {"id": "1", "price": 2000, "in_stock": True},
            {"id": "2", "price": 6000, "in_stock": True},
            {"id": "3", "price": 4500, "in_stock": True}
        ]
        passed, rejected = HardConstraintFilter.apply_hard_constraints(
            dummy_products, {"max_price": 5000}
        )
        self.assertEqual(len(passed), 2)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["product_id"], "2")

    # 5. Test Pattern Exclusion
    def test_pattern_exclusion(self):
        dummy_products = [
            {"id": "1", "pattern": "Solid", "title": "Solid Kurta", "in_stock": True},
            {"id": "2", "pattern": "Floral", "title": "Floral Kurta", "in_stock": True},
            {"id": "3", "pattern": "Solid", "title": "Yellow flower print kurta", "in_stock": True}
        ]
        passed, rejected = HardConstraintFilter.apply_hard_constraints(
            dummy_products, {"excluded_patterns": ["floral"]}
        )
        self.assertEqual(len(passed), 2)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["product_id"], "2")

    # 6. Test Category Filter
    def test_category_filter(self):
        dummy_products = [
            {"id": "1", "category": "Kurtas", "in_stock": True},
            {"id": "2", "category": "Shirts", "in_stock": True}
        ]
        passed, rejected = HardConstraintFilter.apply_hard_constraints(
            dummy_products, {"category": "Kurta"}
        )
        self.assertEqual(len(passed), 1)
        self.assertEqual(passed[0]["id"], "1")

    # 7. Test Score Calculation
    def test_score_calculation(self):
        sample_prod = {
            "id": "T1", "title": "Linen Kurta", "material": "Linen",
            "pattern": "Solid", "occasion": "Wedding", "season": "Summer", "rating": 4.5, "price": 3000, "gender": "Men", "category": "Kurtas"
        }
        soft_intent = {"preferences": ["minimal", "breathable"], "occasion": "wedding", "season": "summer"}
        scored = self.scorer.score_candidate(sample_prod, 0.80, soft_intent)
        self.assertIn("final_score", scored)
        self.assertGreaterEqual(scored["final_score"], 70.0)
        self.assertLessEqual(scored["final_score"], 100.0)
        self.assertEqual(len(scored["score_breakdown"]), 5)

    # 8. Test Ranking Ordering
    def test_ranking(self):
        candidates = [
            ({"id": "low", "title": "P1", "rating": 3.0, "price": 1000, "gender": "Men", "category": "Kurtas"}, 0.30),
            ({"id": "high", "title": "P2", "rating": 4.8, "price": 1000, "gender": "Men", "category": "Kurtas"}, 0.90)
        ]
        ranked = self.scorer.rank_candidates(candidates, {})
        self.assertEqual(ranked[0]["product_id"], "high")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertEqual(ranked[1]["rank"], 2)

    # 9. Test Empty Results & Contradictory Constraints (Edge Case)
    def test_empty_results(self):
        # Budget Rs. 10 is impossible
        res = self.pipeline.run("kurta", hard_constraints={"max_price": 10})
        self.assertEqual(len(res["results"]), 0)
        self.assertGreater(res["rejected_count"], 0)

    # 10. Test API /health Endpoint
    def test_api_health(self):
        with TestClient(app) as client:
            resp = client.get("/health")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "healthy")
            self.assertGreater(data["indexed_products"], 0)

    # 11. Test API /search Endpoint
    def test_api_search(self):
        with TestClient(app) as client:
            payload = {
                "query": "I need a comfortable minimal summer wedding kurta under 5000 with no floral patterns"
            }
            resp = client.post("/search", json=payload)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["query"], payload["query"])
            self.assertGreater(data["filtered_count"], 0)
            self.assertEqual(len(data["results"]), 5)
            # Ensure top result satisfies constraints
            top_result = data["results"][0]
            self.assertLessEqual(top_result["product_details"]["price"], 5000)
            self.assertNotEqual(top_result["product_details"]["pattern"].lower(), "floral")

if __name__ == "__main__":
    unittest.main()
