"""
IntentCart - ML Subsystem
Module: retrieval/preference_matcher.py

Objective (Phase 15):
Calculates explainable soft preference alignment scores across:
- style/comfort preferences (minimal, breathable, comfortable)
- occasion relevance (wedding, formal, festive)
- season/climate suitability (summer, hot weather)
- customer satisfaction rating

All scores are bounded between 0.0 and 1.0.
"""

from typing import Any

# Domain knowledge mappings for textile and garment comfort
BREATHABLE_MATERIALS = {"linen", "cotton", "khadi", "khadi cotton", "chanderi", "viscose"}
WARM_MATERIALS = {"velvet", "wool", "wool blend", "brocade", "fleece"}
MINIMAL_STYLES = {"minimal", "solid", "plain", "classic", "clean"}
FORMAL_OCCASIONS = {"wedding", "formal", "reception", "ceremony", "festive"}

class PreferenceMatcher:
    """
    Computes soft preference scores based on metadata and text alignment.
    These scores reflect degree of relevance, NOT probabilistic predictions.
    """

    @staticmethod
    def score_comfort_and_preferences(product: dict, soft_preferences: list[str]) -> tuple[float, list[str]]:
        """
        Scores how well product attributes match soft preference keywords
        (e.g., 'minimal', 'comfortable', 'breathable', 'lightweight').
        """
        if not soft_preferences:
            return 1.0, []

        matches = []
        material = product.get("material", "").lower()
        style = product.get("style", "")
        style_str = " ".join(style).lower() if isinstance(style, list) else str(style).lower()
        pattern = product.get("pattern", "").lower()
        desc = product.get("description", "").lower()

        score_points = 0.0
        total_prefs = len(soft_preferences)

        for pref in soft_preferences:
            pref_lower = pref.lower().strip()
            
            if pref_lower in ["breathable", "airy", "cool"]:
                if any(m in material for m in BREATHABLE_MATERIALS) or "breathable" in desc or "airy" in desc:
                    score_points += 1.0
                    matches.append(f"Breathable fabric ({product.get('material', 'lightweight')})")
                else:
                    score_points += 0.3  # Partial default for general light apparel
            
            elif pref_lower in ["minimal", "simple", "unembellished"]:
                if pattern == "solid" or any(s in style_str for s in MINIMAL_STYLES) or "minimal" in desc:
                    score_points += 1.0
                    matches.append(f"Minimalist design (Pattern: {product.get('pattern')})")
                else:
                    score_points += 0.2

            elif pref_lower in ["comfortable", "comfy", "soft"]:
                if any(m in material for m in BREATHABLE_MATERIALS) or "comfort" in desc:
                    score_points += 1.0
                    matches.append(f"High comfort material ({product.get('material')})")
                else:
                    score_points += 0.5
            
            else:
                # Generic keyword check across metadata and description
                if pref_lower in desc or pref_lower in style_str:
                    score_points += 1.0
                    matches.append(f"Matches '{pref}' in details")
                else:
                    score_points += 0.2

        final_score = min(1.0, score_points / max(1, total_prefs))
        return round(final_score, 4), matches

    @staticmethod
    def score_occasion(product: dict, target_occasion: str) -> tuple[float, list[str]]:
        """
        Scores how suitable a garment is for a specific event (e.g. 'wedding', 'formal').
        """
        if not target_occasion:
            return 1.0, []

        target_lower = target_occasion.lower().strip()
        prod_occ = product.get("occasion", "")
        occ_str = " ".join(prod_occ).lower() if isinstance(prod_occ, list) else str(prod_occ).lower()
        prod_style = product.get("style", "")
        style_str = " ".join(prod_style).lower() if isinstance(prod_style, list) else str(prod_style).lower()
        title_desc = f"{product.get('title', '')} {product.get('description', '')}".lower()

        # Direct match in occasion field
        if target_lower in occ_str:
            return 1.0, [f"Tailored for {target_occasion}"]

        # Match in style or title/description
        if target_lower in style_str or target_lower in title_desc:
            return 0.85, [f"Suitable for {target_occasion} occasions"]

        # Cross-compatibility check (e.g. formal clothing for a wedding)
        if target_lower == "wedding" and ("formal" in style_str or "formal" in occ_str or "festive" in occ_str):
            return 0.75, ["Formal/festive attire suitable for wedding attendance"]

        # Casual mismatch penalty
        if "casual" in style_str or "casual" in occ_str:
            return 0.25, ["Primarily casual wear; less formal for wedding"]

        return 0.50, [f"Standard suitability for {target_occasion}"]

    @staticmethod
    def score_season(product: dict, target_season: str) -> tuple[float, list[str]]:
        """
        Scores climate / seasonal suitability (e.g. 'summer', 'hot weather').
        """
        if not target_season:
            return 1.0, []

        target_lower = target_season.lower().strip()
        prod_season = product.get("season", "").lower()
        material = product.get("material", "").lower()
        desc = product.get("description", "").lower()

        if target_lower in ["summer", "hot weather", "warm"]:
            # Summer ground truth match
            if "summer" in prod_season or "spring" in prod_season:
                return 1.0, ["Designed specifically for summer season"]
            # Material-derived summer comfort
            if any(m in material for m in BREATHABLE_MATERIALS):
                return 0.90, [f"Summer-appropriate fabric ({product.get('material')})"]
            # Winter heavy fabric penalty
            if any(m in material for m in WARM_MATERIALS) or "winter" in prod_season:
                return 0.15, [f"Heavy winter fabric ({product.get('material')}); unsuited for summer"]
            return 0.50, ["All-season fabric"]

        elif target_lower in ["winter", "cold"]:
            if "winter" in prod_season or any(m in material for m in WARM_MATERIALS):
                return 1.0, ["Designed for cold weather / winter"]
            return 0.40, ["Light fabric"]

        return 0.70, ["Neutral seasonal suitability"]

    @staticmethod
    def score_rating(product: dict) -> float:
        """
        Normalizes 0.0 - 5.0 star ratings into a 0.0 - 1.0 score.
        Defaults to 4.0 (0.80) if rating is absent.
        """
        raw_rating = product.get("rating")
        if raw_rating is None:
            return 0.80
        try:
            val = float(raw_rating)
            return round(min(1.0, max(0.0, val / 5.0)), 4)
        except (ValueError, TypeError):
            return 0.80
