"""
Script: scripts/resolve_all_images.py

Objective:
Resolves real product images and purchase links for products in clean_products.json
using their original Myntra product IDs.
Saves to artifacts/image_cache.json incrementally and updates data/processed/clean_products.json.
"""

import os
import re
import ssl
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PROCESSED_PATH = os.path.join("data", "processed", "clean_products.json")
CACHE_PATH = os.path.join("artifacts", "image_cache.json")

ctx = ssl._create_unverified_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def extract_clean_id(raw_id: str) -> str:
    return str(raw_id).replace("MYN_ST_", "").replace("MYN_", "").strip()

def resolve_product(prod: dict) -> tuple[str, str | None, str]:
    clean_id = extract_clean_id(prod.get("id", ""))
    prod_url = f"https://www.myntra.com/{clean_id}"
    
    # Check if already has a valid full URL with date/hash
    curr_img = prod.get("image_url")
    if curr_img and curr_img != "unknown" and "assets.myntassets.com" in curr_img:
        if not curr_img.endswith(f"{clean_id}.jpg"):
            return clean_id, curr_img, prod_url

    try:
        req = urllib.request.Request(prod_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=3.5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # 1. Look for og:image
            og_imgs = re.findall(r'<meta property="og:image" content="([^"]+)"', html)
            if og_imgs:
                raw_img = og_imgs[0]
                high_res = re.sub(r'h_\d+,w_\d+,c_[^/]+/', '', raw_img)
                return clean_id, high_res, prod_url
            
            # 2. Look for any assets.myntassets.com image
            imgs = re.findall(r'https://assets\.myntassets\.com/(?:[^\s"\'<>]+\.jpg)', html)
            for img in imgs:
                if "/images/" in img and "banners" not in img and "retaillabs" not in img and "msite" not in img:
                    high_res = re.sub(r'h_\d+,w_\d+,c_[^/]+/', '', img)
                    return clean_id, high_res, prod_url
    except Exception:
        pass
        
    return clean_id, None, prod_url

def main():
    print(f"Loading products from: {PROCESSED_PATH}", flush=True)
    with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"Total catalog products: {len(products)}", flush=True)

    cache = {}
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"Loaded existing cache with {len(cache)} entries.", flush=True)
        except Exception:
            cache = {}

    to_resolve = []
    for p in products:
        cid = extract_clean_id(p["id"])
        # If not in cache or cached image is None, retry
        if cid not in cache:
            to_resolve.append(p)

    print(f"Resolving images for {len(to_resolve)} products via ThreadPoolExecutor...", flush=True)

    found = sum(1 for v in cache.values() if v.get("image_url"))
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(resolve_product, p): p for p in to_resolve}
        for idx, fut in enumerate(as_completed(futures), 1):
            cid, img_url, purl = fut.result()
            if img_url:
                cache[cid] = {"image_url": img_url, "product_url": purl}
                found += 1
            else:
                cache[cid] = {"image_url": None, "product_url": purl}

            if idx % 25 == 0 or idx == len(to_resolve):
                print(f"  Processed {idx}/{len(to_resolve)} (Found {found} real images)", flush=True)
                with open(CACHE_PATH, "w", encoding="utf-8") as f:
                    json.dump(cache, f, indent=2)

    # Update clean_products.json with all resolved images and purchase URLs
    updated_count = 0
    for p in products:
        cid = extract_clean_id(p["id"])
        c_entry = cache.get(cid, {})
        p["product_url"] = c_entry.get("product_url", f"https://www.myntra.com/{cid}")
        real_img = c_entry.get("image_url")
        if real_img:
            p["image_url"] = real_img
            updated_count += 1

    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Updated {updated_count} products in clean_products.json with authentic Myntra images & links!", flush=True)

if __name__ == "__main__":
    main()
