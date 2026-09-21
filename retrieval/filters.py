"""
IntentCart - ML Subsystem
Module: retrieval/filters.py

Objective:
Deterministic hard-constraint engine.
Filters product candidates strictly according to non-negotiable requirements:
1. Exact Canonical Category Matching (e.g. 'Shirts' NEVER matches 'T-Shirts' or 'Kurtas')
2. Explicit Gender Compatibility (ONLY when gender is explicitly specified by user)
3. Budget limits (Maximum and Minimum price caps)
4. Stock availability (In-stock only)
5. Negative Constraints (Strict exclusion of forbidden patterns, colors, materials)
"""

from typing import Any, Tuple, List, Dict
from retrieval.category_normalizer import is_category_match, normalize_to_canonical_category

class HardConstraintFilter:
    """
    Evaluates candidates against deterministic hard constraints.
    Returns:
      - passed_products: list of products that satisfy 100% of hard constraints.
      - rejected_records: list of products that failed, with specific failure reasons.
    """

    @staticmethod
    def evaluate_product(product: dict, constraints: dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Evaluates a single product against the given constraints.
        Returns (is_passed, list_of_violations).
        """
        violations = []

        # 1. Exact Category constraint (CRITICAL - Eligibility Determiner)
        target_category = constraints.get("canonical_category") or constraints.get("category")
        if target_category:
            prod_category = product.get("category")
            if not is_category_match(prod_category, target_category):
                canonical_target = normalize_to_canonical_category(target_category) or target_category
                violations.append(
                    f"Category mismatch: Expected '{canonical_target}', found '{prod_category}'"
                )

        # 2. Gender constraint (CRITICAL: Only enforced if gender was EXPLICITLY specified)
        gender_specified = constraints.get("gender_specified")
        target_gender = constraints.get("gender")

        # If gender_specified is None, infer from presence of target_gender
        if gender_specified is None:
            gender_specified = bool(target_gender)

        if gender_specified and target_gender:
            prod_gender = product.get("gender", "").strip().lower()
            target_lower = target_gender.strip().lower()

            if target_lower in ["men", "man", "male"]:
                allowed = ["men", "unisex", "unknown"]
            elif target_lower in ["women", "woman", "female"]:
                allowed = ["women", "unisex", "unknown"]
            elif target_lower in ["boys", "boy"]:
                allowed = ["boys", "men", "unisex", "unknown"]
            elif target_lower in ["girls", "girl"]:
                allowed = ["girls", "women", "unisex", "unknown"]
            else:
                allowed = [target_lower, "unisex", "unknown"]

            if prod_gender not in allowed:
                violations.append(
                    f"Gender mismatch: Expected '{target_gender}', found '{product.get('gender')}'"
                )

        # 3. Maximum price constraint (budget limit)
        max_price = constraints.get("max_price")
        if max_price is not None:
            price = product.get("price", 0)
            if price > max_price:
                violations.append(f"Price Rs.{price} exceeds maximum budget Rs.{max_price}")

        # 4. Minimum price constraint
        min_price = constraints.get("min_price")
        if min_price is not None:
            price = product.get("price", 0)
            if price < min_price:
                violations.append(f"Price Rs.{price} is below minimum Rs.{min_price}")

        # 5. Stock constraint (in-stock only)
        if constraints.get("in_stock_only", True):
            is_in_stock = product.get("in_stock")
            if is_in_stock is None:
                is_in_stock = product.get("stock", 0) > 0
            elif isinstance(is_in_stock, bool):
                if "stock" in product and product["stock"] == 0:
                    is_in_stock = False

            if not is_in_stock:
                violations.append(f"Out of stock (stock: {product.get('stock', 0)})")

        # 6. Negative constraints (Forbidden patterns, colors, materials)
        excluded_patterns = list(constraints.get("excluded_patterns", []))
        excluded_materials = list(constraints.get("excluded_materials", []))
        excluded_colors = list(constraints.get("excluded_colors", []))

        # Also parse raw negative_constraints if passed
        for neg in constraints.get("negative_constraints", []):
            neg_clean = neg.lower().replace("no ", "").replace("not ", "").replace("without ", "").strip()
            if "floral" in neg_clean and "floral" not in excluded_patterns:
                excluded_patterns.append("floral")
            elif "stripe" in neg_clean and "stripe" not in excluded_patterns:
                excluded_patterns.append("stripe")

        prod_pattern = product.get("pattern", "").strip().lower()
        prod_material = product.get("material", "").strip().lower()
        prod_color = product.get("color", "").strip().lower()
        title_desc = f"{product.get('title', '')} {product.get('description', '')}".lower()

        # Check pattern exclusions
        for exc in excluded_patterns:
            exc_lower = exc.strip().lower()
            if exc_lower == prod_pattern or exc_lower in title_desc:
                violations.append(f"Negative preference violation: Contains excluded pattern '{exc}'")
                break

        # Check material exclusions
        for exc in excluded_materials:
            exc_lower = exc.strip().lower()
            if exc_lower == prod_material or exc_lower in title_desc:
                violations.append(f"Negative preference violation: Contains excluded material '{exc}'")
                break

        # Check color exclusions
        for exc in excluded_colors:
            exc_lower = exc.strip().lower()
            if exc_lower == prod_color or exc_lower in title_desc:
                violations.append(f"Negative preference violation: Contains excluded color '{exc}'")
                break

        is_passed = (len(violations) == 0)
        return is_passed, violations

    @classmethod
    def apply_hard_constraints(
        cls, products: list[dict], constraints: dict[str, Any]
    ) -> Tuple[list[dict], list[dict]]:
        """
        Applies hard constraints across a collection of products.
        Returns:
            passed_products: list of products passing all constraints.
            rejected_records: list of dicts: {'product_id': id, 'title': title, 'reasons': violations}.
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
