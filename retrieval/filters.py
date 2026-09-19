"""
IntentCart - ML Subsystem
Module: retrieval/filters.py

Objective (Phase 14):
Deterministic hard-constraint engine.
Filters product candidates strictly according to non-negotiable requirements
(budget limits, stock availability, gender, pattern exclusions).
"""

from typing import Any

class HardConstraintFilter:
    """
    Evaluates candidates against deterministic hard constraints.
    Returns:
      - passed_products: list of products that satisfy 100% of hard constraints.
      - rejected_records: list of products that failed, with specific failure reasons.
    """

    @staticmethod
    def evaluate_product(product: dict, constraints: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Evaluates a single product against the given constraints.
        Returns (is_passed, list_of_violations).
        """
        violations = []

        # 1. Stock constraint (in-stock only)
        if constraints.get("in_stock_only", True):
            # Check boolean in_stock if present; also check numeric stock if present
            is_in_stock = product.get("in_stock")
            if is_in_stock is None:
                # If boolean in_stock is missing, fall back to numeric stock count
                is_in_stock = product.get("stock", 0) > 0
            elif isinstance(is_in_stock, bool):
                # Also check numeric stock if explicitly 0
                if "stock" in product and product["stock"] == 0:
                    is_in_stock = False

            if not is_in_stock:
                violations.append(f"Out of stock (stock: {product.get('stock', 0)})")

        # 2. Maximum price constraint (budget limit)
        max_price = constraints.get("max_price")
        if max_price is not None:
            price = product.get("price", 0)
            if price > max_price:
                violations.append(f"Price Rs.{price} exceeds maximum budget Rs.{max_price}")

        # 3. Minimum price constraint
        min_price = constraints.get("min_price")
        if min_price is not None:
            price = product.get("price", 0)
            if price < min_price:
                violations.append(f"Price Rs.{price} is below minimum Rs.{min_price}")

        # 4. Gender constraint
        target_gender = constraints.get("gender")
        if target_gender:
            prod_gender = product.get("gender", "").strip().lower()
            target_lower = target_gender.strip().lower()
            if prod_gender not in [target_lower, "unisex", "unknown"]:
                violations.append(f"Gender '{product.get('gender')}' does not match target '{target_gender}'")

        # 5. Category constraint
        target_category = constraints.get("category")
        if target_category:
            prod_category = product.get("category", "").strip().lower()
            target_cat_lower = target_category.strip().lower()
            if target_cat_lower not in prod_category:
                violations.append(f"Category '{product.get('category')}' does not match target '{target_category}'")

        # 6. Excluded patterns (e.g. 'no floral')
        excluded_patterns = constraints.get("excluded_patterns", [])
        if excluded_patterns:
            prod_pattern = product.get("pattern", "").strip().lower()
            title_desc = f"{product.get('title', '')} {product.get('description', '')}".lower()
            for exc in excluded_patterns:
                exc_lower = exc.strip().lower()
                if exc_lower == prod_pattern or exc_lower in title_desc:
                    violations.append(f"Contains excluded pattern '{exc}'")
                    break

        # 7. Required pattern (if explicitly demanded as hard requirement)
        required_patterns = constraints.get("required_patterns", [])
        if required_patterns:
            prod_pattern = product.get("pattern", "").strip().lower()
            if not any(req.strip().lower() in prod_pattern for req in required_patterns):
                violations.append(f"Missing required pattern in {required_patterns}")

        is_passed = (len(violations) == 0)
        return is_passed, violations

    @classmethod
    def apply_hard_constraints(
        cls, products: list[dict], constraints: dict[str, Any]
    ) -> tuple[list[dict], list[dict]]:
        """
        Applies hard constraints across a collection of products.
        Returns:
            passed_products: list of products passing all constraints.
            rejected_records: list of dicts: {'product': product, 'reasons': violations}.
        """
        passed_products = []
        rejected_records = []

        for p in products:
            is_valid, violations = cls.evaluate_product(p, constraints)
            if is_valid:
                passed_products.append(p)
            else:
                rejected_records.append({
                    "product_id": p.get("id"),
                    "title": p.get("title"),
                    "reasons": violations
                })

        return passed_products, rejected_records


def _run_self_tests():
    """Runs deterministic unit verification of the hard filter engine."""
    import json
    import os

    print("Running Hard Constraint Filter Self-Tests...")
    
    # Load controlled dataset
    demo_path = os.path.join("data", "demo_products.json")
    with open(demo_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # Test 1: Floral Exclusion
    constraints_no_floral = {"excluded_patterns": ["floral"]}
    passed, rejected = HardConstraintFilter.apply_hard_constraints(products, constraints_no_floral)
    print(f"\n[Test 1: Exclude Floral]")
    print(f"  Input products: {len(products)}")
    print(f"  Passed products: {len(passed)}")
    print(f"  Rejected products: {len(rejected)}")
    for r in rejected:
        print(f"    - Rejected {r['product_id']}: {r['reasons']}")
    assert all("floral" not in p.get("pattern", "").lower() for p in passed)

    # Test 2: Price budget under Rs. 5000
    constraints_budget = {"max_price": 5000}
    passed_budget, rejected_budget = HardConstraintFilter.apply_hard_constraints(products, constraints_budget)
    print(f"\n[Test 2: Budget <= Rs. 5,000]")
    print(f"  Passed: {len(passed_budget)} | Rejected: {len(rejected_budget)}")
    assert all(p["price"] <= 5000 for p in passed_budget)

    # Test 3: In-Stock Only
    constraints_stock = {"in_stock_only": True}
    passed_stock, rejected_stock = HardConstraintFilter.apply_hard_constraints(products, constraints_stock)
    print(f"\n[Test 3: In Stock Only]")
    print(f"  Passed: {len(passed_stock)} | Rejected: {len(rejected_stock)}")
    assert all(p.get("stock", 1) > 0 for p in passed_stock)
    assert any(r["product_id"] == "PROD_009" for r in rejected_stock)

    # Test 4: Full Multi-Constraint Scenario:
    # "Men's Kurta, under Rs.5000, in stock, NO floral"
    multi_constraints = {
        "gender": "Men",
        "category": "Kurta",
        "max_price": 5000,
        "in_stock_only": True,
        "excluded_patterns": ["floral"]
    }
    passed_multi, rejected_multi = HardConstraintFilter.apply_hard_constraints(products, multi_constraints)
    print(f"\n[Test 4: Full Multi-Constraint Query]")
    print(f"  Constraints: {multi_constraints}")
    print(f"  Passed: {len(passed_multi)} products:")
    for p in passed_multi:
        print(f"    [PASS] [{p['id']}] Rs.{p['price']} | {p['pattern']} | {p['material']} | {p['title']}")

    print("\nAll Hard Constraint Self-Tests PASSED successfully.")

if __name__ == "__main__":
    _run_self_tests()
