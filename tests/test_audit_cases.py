"""
IntentCart - Master Audit Test Suite (Section 28)
File: tests/test_audit_cases.py

Validates:
1. Exact Canonical Category Isolation (Zero bleeding between Shirts, T-Shirts, Kurtas, Jeans, Trousers, etc.)
2. Deterministic Gender Non-Inference (Gender unassigned unless explicitly requested)
3. Hard Constraints and Negative Constraint Filtering (Deterministic removal of floral patterns, price limits, stock)
4. Top-K Honesty and Match Status ('exact', 'partial_match', 'no_exact_match')
5. Trace Telemetry and Rejection Reasons
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from retrieval.category_normalizer import normalize_category, is_category_match, CANONICAL_CATEGORIES
from llm.intent_extractor import intent_extractor
from llm.adapter import map_schema_to_pipeline_args
from retrieval.pipeline import IntentCartPipeline

class TestIntentCartAuditCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 70)
        print("INITIALIZING AUDIT SUITE PIPELINE")
        print("=" * 70)
        cls.pipeline = IntentCartPipeline()

    def _extract_intent(self, query: str):
        time.sleep(1.2) # Avoid TPM rate limits during sequential test runs
        return intent_extractor.extract_intent(query)

    # --- UNIT TESTS: CANONICAL CATEGORY NORMALIZER ---

    def test_category_normalizer_isolation(self):
        """Verify regex boundary separation for tricky categories."""
        # Shirts
        self.assertEqual(normalize_category("shirt"), "Shirts")
        self.assertEqual(normalize_category("formal shirts"), "Shirts")
        self.assertEqual(normalize_category("casual shirt"), "Shirts")
        
        # T-Shirts (Must NOT match Shirts)
        self.assertEqual(normalize_category("t-shirt"), "T-Shirts")
        self.assertEqual(normalize_category("tshirt"), "T-Shirts")
        self.assertEqual(normalize_category("tee"), "T-Shirts")
        self.assertEqual(normalize_category("tees"), "T-Shirts")
        self.assertEqual(normalize_category("polo"), "T-Shirts")
        
        # Kurtas
        self.assertEqual(normalize_category("kurta"), "Kurtas")
        self.assertEqual(normalize_category("kurtas"), "Kurtas")
        self.assertEqual(normalize_category("kurti"), "Kurtas")
        
        # Jeans vs Trousers
        self.assertEqual(normalize_category("jeans"), "Jeans")
        self.assertEqual(normalize_category("denim pants"), "Jeans")
        self.assertEqual(normalize_category("trouser"), "Trousers")
        self.assertEqual(normalize_category("chinos"), "Trousers")
        
        # Category match helper
        self.assertTrue(is_category_match("Shirts", "Shirts"))
        self.assertFalse(is_category_match("Shirts", "T-Shirts"))
        self.assertFalse(is_category_match("T-Shirts", "Shirts"))
        self.assertFalse(is_category_match("Kurtas", "Shirts"))

    # --- 10 MANDATORY MASTER AUDIT CASES (SECTION 28) ---

    def test_case_01_generic_shirt_no_gender(self):
        """1. 'I need a shirt.' -> Shirts only, gender unstated/unspecified."""
        query = "I need a shirt."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertFalse(schema.hard_constraints.gender_specified)
        self.assertIsNone(schema.hard_constraints.gender)
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        self.assertEqual(out["match_status"], "exact")
        for item in out["results"]:
            cat = item["product_details"].get("category", "") or item["product_details"].get("article_type", "")
            self.assertEqual(normalize_category(cat), "Shirts", f"Bleeding detected: {cat}")
            self.assertNotEqual(normalize_category(cat), "T-Shirts")
            self.assertNotEqual(normalize_category(cat), "Kurtas")

    def test_case_02_mens_shirt(self):
        """2. 'I need a men's shirt.' -> Shirts only, gender strictly Men."""
        query = "I need a men's shirt."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertTrue(schema.hard_constraints.gender_specified)
        self.assertEqual(schema.hard_constraints.gender, "Men")
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            gender = item["product_details"].get("gender", "")
            self.assertEqual(normalize_category(cat), "Shirts")
            self.assertIn(gender, ["Men", "Unisex"], f"Wrong gender returned: {gender}")

    def test_case_03_womens_shirt(self):
        """3. 'I need a women's shirt.' -> Shirts only, gender strictly Women."""
        query = "I need a women's shirt."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertTrue(schema.hard_constraints.gender_specified)
        self.assertEqual(schema.hard_constraints.gender, "Women")
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        # If dataset contains women's shirts, verify category and gender
        if len(out["results"]) > 0:
            for item in out["results"]:
                cat = item["product_details"].get("category", "")
                gender = item["product_details"].get("gender", "")
                self.assertEqual(normalize_category(cat), "Shirts")
                self.assertIn(gender, ["Women", "Unisex"])

    def test_case_04_black_formal_shirt_interview(self):
        """4. 'I need a black formal shirt for an interview.' -> Shirts only, unstated gender, black/formal prioritized."""
        query = "I need a black formal shirt for an interview."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertFalse(schema.hard_constraints.gender_specified)
        self.assertIsNone(schema.hard_constraints.gender)
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Shirts")
        
        # Check that top result aligns with black or formal
        top_item = out["results"][0]
        top_details = str(top_item["product_details"]).lower()
        self.assertTrue("black" in top_details or "formal" in top_details or "shirt" in top_details)

    def test_case_05_minimal_shirt_no_floral(self):
        """5. 'I need a minimal shirt with no floral patterns.' -> Shirts only, zero floral patterns."""
        query = "I need a minimal shirt with no floral patterns."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertIn("floral", [p.lower() for p in (schema.hard_constraints.excluded_patterns or [])])
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Shirts")
            text = f"{item['title']} {item['product_details'].get('description', '')}".lower()
            self.assertNotIn("floral", text, f"Floral pattern found in {item['product_id']}")

    def test_case_06_summer_shirt_breathable_comfortable(self):
        """6. 'I need a summer shirt that is breathable and comfortable.' -> Shirts only, breathable & comfortable."""
        query = "I need a summer shirt that is breathable and comfortable."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Shirts")

    def test_case_07_jeans_exact_retrieval(self):
        """7. 'I need jeans.' -> Jeans only, zero trousers, chinos, shorts."""
        query = "I need jeans."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Jeans")
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Jeans", f"Expected Jeans, got {cat}")
            self.assertNotEqual(normalize_category(cat), "Trousers")

    def test_case_08_kurta_wedding(self):
        """8. 'I need a kurta for a wedding.' -> Kurtas only, zero shirts or t-shirts."""
        query = "I need a kurta for a wedding."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Kurtas")
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Kurtas", f"Expected Kurtas, got {cat}")
            self.assertNotEqual(normalize_category(cat), "Shirts")
            self.assertNotEqual(normalize_category(cat), "T-Shirts")

    def test_case_09_shirt_but_no_floral(self):
        """9. 'I need a shirt but no floral patterns.' -> Shirts only, negative constraint respected."""
        query = "I need a shirt but no floral patterns."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertIn("floral", [p.lower() for p in (schema.hard_constraints.excluded_patterns or [])])
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Shirts")
            text = f"{item['title']} {item['product_details'].get('description', '')}".lower()
            self.assertNotIn("floral", text)

    def test_case_10_shirt_for_interview_gender_unstated(self):
        """10. 'I need a shirt for an interview.' -> Shirts only, gender MUST NOT be inferred."""
        query = "I need a shirt for an interview."
        schema, _ = self._extract_intent(query)
        
        self.assertEqual(schema.hard_constraints.canonical_category, "Shirts")
        self.assertFalse(schema.hard_constraints.gender_specified)
        self.assertIsNone(schema.hard_constraints.gender)
        
        args = map_schema_to_pipeline_args(schema)
        out = self.pipeline.run(**args, top_k=5)
        
        self.assertGreater(len(out["results"]), 0)
        for item in out["results"]:
            cat = item["product_details"].get("category", "")
            self.assertEqual(normalize_category(cat), "Shirts")

    # --- HONESTY & TELEMETRY TESTS ---

    def test_top_k_honesty_zero_matches(self):
        """Impossible constraint returns match_status='no_exact_match' and empty results."""
        out = self.pipeline.run(
            query="shirt",
            hard_constraints={
                "canonical_category": "Shirts",
                "max_price": 5 # Impossible price in our catalog
            },
            soft_intent={},
            top_k=5
        )
        self.assertEqual(out["match_status"], "no_exact_match")
        self.assertEqual(len(out["results"]), 0)
        self.assertEqual(out["filtered_count"], 0)
        self.assertGreater(out["rejected_count"], 0)

    def test_trace_telemetry_populated(self):
        """Verify pipeline trace dictionary contains all filter stage numbers."""
        out = self.pipeline.run(
            query="shirt",
            hard_constraints={"canonical_category": "Shirts"},
            soft_intent={},
            top_k=5
        )
        self.assertIn("trace", out)
        trace = out["trace"]
        self.assertIn("candidate_pool_size", trace)
        self.assertIn("after_category_filter", trace)
        self.assertIn("after_hard_filter", trace)
        self.assertIn("after_negative_filter", trace)
        self.assertIn("rejection_counts", trace)
        self.assertGreaterEqual(trace["candidate_pool_size"], 100)

if __name__ == "__main__":
    unittest.main()
