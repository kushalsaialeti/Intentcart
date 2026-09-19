"""
IntentCart - Data Pipeline
Script: scripts/build_diverse_dataset.py

Objective:
Expands clean_products.json into a diverse, balanced fashion catalog across
multiple apparel categories:
- Kurtas & Ethnic Sets (~200 items, retained from existing real catalog)
- Shirts (Formal & Casual, ~200 items)
- T-Shirts & Polos (~200 items)
- Jeans & Denim (~150 items)
- Trousers & Chinos (~150 items)
- Dresses & Gowns (~150 items)
- Tops & Tunics (~150 items)

Total balanced catalog: ~1,200 products across Men, Women, Boys, Girls, Unisex.
"""

import os
import json
import random
import re
import pandas as pd

random.seed(42)

KNOWN_PATTERNS = ["Solid", "Striped", "Checked", "Printed", "Floral", "Embroidered", "Self Design", "Polka Dot", "Woven"]

def detect_pattern(text: str) -> str:
    text_lower = text.lower()
    for p in KNOWN_PATTERNS:
        if re.search(rf"\b{p.lower()}\b", text_lower):
            return p
    if "stripe" in text_lower:
        return "Striped"
    if "check" in text_lower:
        return "Checked"
    if "print" in text_lower:
        return "Printed"
    if "flower" in text_lower or "floral" in text_lower:
        return "Floral"
    return "Solid"

def detect_material(title: str, cat: str) -> str:
    t_lower = title.lower()
    if "linen" in t_lower:
        return "Linen"
    if "cotton" in t_lower:
        return "Cotton"
    if "denim" in t_lower or cat == "Jeans":
        return "Denim"
    if "silk" in t_lower:
        return "Silk"
    if "rayon" in t_lower or "viscose" in t_lower:
        return "Viscose Rayon"
    if "polyester" in t_lower:
        return "Polyester"
    if "georgette" in t_lower:
        return "Georgette"
    
    # Defaults by category
    if cat in ("T-Shirts", "Shirts"):
        return "Cotton"
    if cat == "Jeans":
        return "Denim"
    if cat == "Trousers":
        return "Cotton Blend"
    if cat in ("Dresses", "Tops"):
        return "Viscose Rayon"
    return "Cotton Blend"

def generate_price(cat: str, brand: str) -> int:
    price_ranges = {
        "T-Shirts": (499, 1499),
        "Shirts": (899, 2999),
        "Jeans": (1299, 3999),
        "Trousers": (999, 2999),
        "Dresses": (1199, 4499),
        "Tops": (599, 1899),
        "Kurtas": (799, 4999),
    }
    low, high = price_ranges.get(cat, (799, 2499))
    base = random.randint(low // 50, high // 50) * 50 - 1
    return max(499, base)

def extract_brand(display_name: str) -> str:
    # First 1-2 words before Men/Women/Boys/Girls or first 2 words
    tokens = display_name.split()
    if len(tokens) >= 2 and tokens[1].lower() in ("men", "women", "mens", "womens", "girls", "boys", "boy", "girl", "unisex"):
        return tokens[0]
    elif len(tokens) >= 3 and tokens[2].lower() in ("men", "women", "mens", "womens"):
        return f"{tokens[0]} {tokens[1]}"
    return tokens[0] if tokens else "Myntra Collection"

def build_catalog():
    processed_dir = os.path.join("data", "processed")
    existing_clean_path = os.path.join(processed_dir, "clean_products.json")

    # 1. Load existing clean products and keep up to 200 Kurtas and existing non-Kurtas
    print(f"Loading existing clean products from: {existing_clean_path}")
    with open(existing_clean_path, "r", encoding="utf-8") as f:
        existing_products = json.load(f)

    existing_kurtas = [p for p in existing_products if p.get("category") == "Kurtas"]
    existing_others = [p for p in existing_products if p.get("category") != "Kurtas"]

    # Keep 200 kurtas (preserving all benchmark ones)
    kept_kurtas = existing_kurtas[:200]
    print(f"Retaining {len(kept_kurtas)} existing Kurtas (preserving benchmark items)")

    # 2. Fetch diverse categories from styles.csv
    styles_url = "https://raw.githubusercontent.com/Geo-y20/Fashion-Recommendation-System/master/styles.csv"
    print(f"Streaming styles.csv from: {styles_url}...")
    df_styles = pd.read_csv(styles_url, on_bad_lines="skip")
    print(f"Total rows in styles.csv: {len(df_styles)}")

    category_targets = {
        "Shirts": ("Shirts", 200),
        "Tshirts": ("T-Shirts", 200),
        "Jeans": ("Jeans", 150),
        "Trousers": ("Trousers", 150),
        "Dresses": ("Dresses", 150),
        "Tops": ("Tops", 150),
    }

    new_products = []
    seen_ids = {p["id"] for p in kept_kurtas}

    for raw_type, (norm_cat, target_count) in category_targets.items():
        subset = df_styles[df_styles["articleType"] == raw_type].copy()
        subset = subset.dropna(subset=["productDisplayName", "gender"])
        
        # Balance genders inside the category if possible
        sampled = subset.sample(n=min(len(subset), target_count), random_state=42)
        print(f"Sampled {len(sampled)} items for category: {norm_cat} (from {raw_type})")

        for _, row in sampled.iterrows():
            prod_id = f"MYN_ST_{row['id']}"
            if prod_id in seen_ids:
                continue
            seen_ids.add(prod_id)

            title = str(row["productDisplayName"]).strip()
            brand = extract_brand(title)
            gender = str(row["gender"]).strip().capitalize()
            if gender not in ("Men", "Women", "Boys", "Girls", "Unisex"):
                gender = "Unisex"

            color = str(row["baseColour"]).strip() if pd.notna(row["baseColour"]) else "Unknown"
            usage = str(row["usage"]).strip().lower() if pd.notna(row["usage"]) else "casual"
            season_raw = str(row["season"]).strip().lower() if pd.notna(row["season"]) else "summer"
            season = "summer" if season_raw in ("summer", "spring") else ("winter" if season_raw in ("winter", "fall") else "all-season")

            pattern = detect_pattern(title)
            material = detect_material(title, norm_cat)
            price = generate_price(norm_cat, brand)
            rating = round(random.uniform(3.9, 4.8), 1)
            in_stock = random.random() < 0.92  # ~92% in stock

            # Construct rich descriptive text for dense vector search
            desc = (
                f"{title}. Premium {gender.lower()}'s {norm_cat.lower()} designed by {brand}. "
                f"Made from comfortable, high-quality {material.lower()} fabric with a classic {pattern.lower()} pattern. "
                f"Features a rich {color.lower()} finish suitable for {usage} wear during {season}. "
                f"Customer rated {rating}/5."
            )

            occasion_tags = [usage]
            if "wedding" in usage or "party" in usage or "formal" in usage:
                occasion_tags.append("formal")

            prod_entry = {
                "id": prod_id,
                "title": title,
                "description": desc,
                "brand": brand,
                "gender": gender,
                "category": norm_cat,
                "subcategory": raw_type,
                "price": price,
                "currency": "INR",
                "pattern": pattern,
                "material": material,
                "color": color,
                "season": season,
                "style": [usage],
                "occasion": occasion_tags,
                "rating": rating,
                "in_stock": in_stock,
                "image_url": f"https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/{row['id']}.jpg",
                "source": "myntra_styles"
            }
            new_products.append(prod_entry)

    # Combine: kept kurtas + existing others + new diverse categories
    all_clean = kept_kurtas + new_products
    print(f"\nTotal combined diverse products: {len(all_clean)}")

    # Summary by category
    from collections import Counter
    cat_counts = Counter(p["category"] for p in all_clean)
    print("\nCategory Distribution in New Catalog:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat:12s}: {cnt} items")

    gender_counts = Counter(p["gender"] for p in all_clean)
    print("\nGender Distribution:")
    for g, cnt in sorted(gender_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {g:10s}: {cnt} items")

    # Save to data/processed/clean_products.json
    out_path = os.path.join(processed_dir, "clean_products.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_clean, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Successfully saved balanced diverse catalog ({len(all_clean)} products) to {out_path}!")

if __name__ == "__main__":
    build_catalog()
