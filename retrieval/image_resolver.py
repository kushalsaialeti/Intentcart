"""
Utility to resolve real Myntra images and product links using product IDs.
"""
import os
import re
import ssl
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

CACHE_PATH = os.path.join("artifacts", "image_cache.json")
ctx = ssl._create_unverified_context()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def extract_clean_id(raw_id: str) -> str:
    return str(raw_id).replace("MYN_ST_", "").replace("MYN_", "").strip()

def resolve_single_product(clean_id: str) -> tuple[str, str | None, str]:
    """
    Returns (clean_id, high_res_img_url, product_page_url)
    """
    prod_url = f"https://www.myntra.com/{clean_id}"
    try:
        req = urllib.request.Request(prod_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # Find og:image
            og_imgs = re.findall(r'<meta property="og:image" content="([^"]+)"', html)
            if og_imgs:
                raw_img = og_imgs[0]
                # If there's a thumbnail crop prefix, remove it to get full resolution
                high_res = re.sub(r'h_\d+,w_\d+,c_[^/]+/', '', raw_img)
                return clean_id, high_res, prod_url
            
            # Look for any assets.myntassets.com image
            imgs = re.findall(r'https://assets\.myntassets\.com/(?:[^\s"\'<>]+\.jpg)', html)
            for img in imgs:
                if "/images/" in img and "banners" not in img and "retaillabs" not in img:
                    high_res = re.sub(r'h_\d+,w_\d+,c_[^/]+/', '', img)
                    return clean_id, high_res, prod_url
    except Exception:
        pass
    
    return clean_id, None, prod_url
