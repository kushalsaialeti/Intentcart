"""
IntentCart - Retrieval & Taxonomy Layer
Module: retrieval/category_normalizer.py

Objective:
Canonical product taxonomy mapping and strict category normalization.
Guarantees:
1. Exact category isolation (e.g. 'Shirts' is STRICTLY isolated from 'T-Shirts', 'Kurtas', etc.).
2. Normalizes user input variations ('shirt', 'formal shirt', 'casual shirts' -> 'Shirts').
3. Normalizes dataset categories to canonical forms.
4. Prevents substring matching bugs ('shirt' will never match 't-shirt').
"""

import re
from typing import Optional, Set

# Canonical categories in the IntentCart catalog
CANONICAL_CATEGORIES = {
    "Shirts",
    "T-Shirts",
    "Kurtas",
    "Jeans",
    "Trousers",
    "Dresses",
    "Tops"
}

# Explicit keyword and regex mapping rules to canonical categories
# Order is critical: more specific expressions (e.g. 't-shirt', 'polo') are evaluated before generic ('shirt')
CATEGORY_MAPPING_RULES = [
    # T-Shirts / Polos (must be checked BEFORE Shirt)
    (r"\b(t[- ]?shirts?|tees?|polo[- ]?shirts?|polos?|graphic[- ]?tees?)\b", "T-Shirts"),
    
    # Shirts (pure button-down, formal, casual, oxford shirts)
    (r"\b(shirts?|formal[- ]?shirts?|casual[- ]?shirts?|oxford[- ]?shirts?|button[- ]?downs?)\b", "Shirts"),
    
    # Kurtas / Ethnic tops
    (r"\b(kurtas?|kurtis?|sherwanis?|kurta[- ]?sets?|churidars?)\b", "Kurtas"),
    
    # Jeans / Denim pants
    (r"\b(jeans?|denims?|skinny[- ]?jeans?|straight[- ]?jeans?|bootcut)\b", "Jeans"),
    
    # Trousers / Chinos / Pants (strictly distinct from Jeans)
    (r"\b(trousers?|chinos?|pants?|formal[- ]?trousers?|slacks?|cargo[- ]?pants?)\b", "Trousers"),
    
    # Dresses / Gowns / Frocks
    (r"\b(dresses?|maxi[- ]?dresses?|gowns?|frocks?|sundresses?)\b", "Dresses"),
    
    # Tops / Blouses / Tunics
    (r"\b(tops?|blouses?|tunics?|crop[- ]?tops?)\b", "Tops")
]


def normalize_to_canonical_category(raw_category: Optional[str]) -> Optional[str]:
    """
    Maps an arbitrary user or LLM category string to a canonical catalog category.
    Returns None if no canonical category matches.
    """
    if not raw_category or not str(raw_category).strip():
        return None
        
    cleaned = str(raw_category).strip().lower()
    
    # Direct canonical lookup (case-insensitive)
    for canonical in CANONICAL_CATEGORIES:
        if cleaned == canonical.lower() or cleaned == canonical.lower().rstrip("s"):
            return canonical

    # Rule-based regex matching
    for pattern, canonical in CATEGORY_MAPPING_RULES:
        if re.search(pattern, cleaned):
            return canonical

    return None


normalize_category = normalize_to_canonical_category


def extract_category_from_query(query: str) -> Optional[str]:
    """
    Deterministically detects if the user explicitly mentioned a canonical category in their query.
    Used to safeguard against LLM omissions or hallucinations.
    """
    if not query:
        return None
        
    q_lower = query.lower()
    for pattern, canonical in CATEGORY_MAPPING_RULES:
        if re.search(pattern, q_lower):
            return canonical
            
    return None


def is_category_match(product_category: Optional[str], requested_category: Optional[str]) -> bool:
    """
    Strict, deterministic category equality verification.
    Guarantees 'shirt' NEVER matches 't-shirt' or 'kurta'.
    
    Args:
        product_category: Category field from product metadata (e.g. 'Shirts', 'T-Shirts')
        requested_category: Category from user intent (e.g. 'Shirt', 'Shirts', 't-shirt')
    Returns:
        bool: True only if both map to the exact same canonical category.
    """
    if not requested_category:
        return True # No category restriction specified
        
    canonical_target = normalize_to_canonical_category(requested_category)
    if not canonical_target:
        # If user asked for an unknown category, compare clean string equality
        return str(product_category).strip().lower() == str(requested_category).strip().lower()

    canonical_prod = normalize_to_canonical_category(product_category)
    return canonical_prod == canonical_target
