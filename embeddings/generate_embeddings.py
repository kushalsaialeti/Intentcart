"""
IntentCart - ML Subsystem
Script: embeddings/generate_embeddings.py

Objective (Phase 13):
1. Load clean_products.json from data/processed/.
2. Transform products into semantically dense searchable text.
3. Compute L2-normalized 384-d float32 embeddings via all-MiniLM-L6-v2.
4. Construct and populate FAISS IndexFlatIP.
5. Persist the complete artifact set:
     - artifacts/product_embeddings.npy
     - artifacts/product_index.faiss
     - artifacts/product_metadata.json
6. Verify and document the exact 1-to-1 index-to-metadata mapping.
"""

import json
import os
import sys
import numpy as np
import faiss

# Support local imports whether invoked from repo root or package folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from embeddings.model_loader import get_embedding_model

def product_to_searchable_text(product: dict) -> str:
    """
    Transforms canonical product attributes into a rich text representation
    specifically tailored for transformer semantic retrieval.
    """
    parts = [
        f"Product: {product.get('title', '')}",
        f"Brand: {product.get('brand', '')}",
        f"Category: {product.get('gender', '')} {product.get('category', '')} - {product.get('subcategory', '')}",
        f"Material: {product.get('material', '')}",
        f"Pattern: {product.get('pattern', '')}",
        f"Color: {product.get('color', '')}",
        f"Description: {product.get('description', '')}"
    ]
    return " | ".join(parts)

def generate_and_save_artifacts():
    # 1. Resolve paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    clean_data_path = os.path.join(base_dir, "data", "processed", "clean_products.json")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    emb_out_path = os.path.join(artifacts_dir, "product_embeddings.npy")
    faiss_out_path = os.path.join(artifacts_dir, "product_index.faiss")
    meta_out_path = os.path.join(artifacts_dir, "product_metadata.json")

    print(f"Loading cleaned products from: {clean_data_path}...")
    with open(clean_data_path, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"Total products loaded: {len(products)}")

    # 2. Convert to searchable text
    print("Generating searchable text for all products...")
    searchable_texts = [product_to_searchable_text(p) for p in products]

    # Preview first representation
    print("\n--- Sample Representation (Product 0) ---")
    print(searchable_texts[0][:200] + "...")
    print("-" * 60 + "\n")

    # 3. Load embedding model
    model = get_embedding_model()

    # 4. Generate normalized embeddings in float32
    print(f"Encoding {len(searchable_texts)} products into 384-d vectors (batch processing)...")
    embeddings = model.encode(
        searchable_texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    embeddings = embeddings.astype(np.float32)

    # 5. Build FAISS IndexFlatIP
    dimension = embeddings.shape[1]
    print(f"\nBuilding FAISS IndexFlatIP (dimension={dimension})...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    print(f"FAISS index built. Total indexed vectors: {index.ntotal}")

    # 6. Save all 3 artifacts
    print(f"\nSaving artifacts to {artifacts_dir}:")
    
    # a. Embeddings NumPy array
    np.save(emb_out_path, embeddings)
    print(f"  [OK] Saved embeddings: {emb_out_path} ({os.path.getsize(emb_out_path):,} bytes)")

    # b. FAISS index binary
    faiss.write_index(index, faiss_out_path)
    print(f"  [OK] Saved FAISS index: {faiss_out_path} ({os.path.getsize(faiss_out_path):,} bytes)")

    # c. Product metadata JSON (MUST strictly mirror index ordering)
    with open(meta_out_path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved metadata: {meta_out_path} ({len(products)} records)")

    # 7. Verification of 1-to-1 Mapping Invariant
    print("\n--- Verifying Index-to-Metadata 1-to-1 Mapping ---")
    print(f"Embedding rows: {embeddings.shape[0]}")
    print(f"FAISS index ntotal: {index.ntotal}")
    print(f"Metadata list length: {len(products)}")
    assert embeddings.shape[0] == index.ntotal == len(products), "MISMATCH: Index ordering violated!"

    # Spot check: vector at index 42 matches product at index 42
    spot_idx = 42
    print(f"Spot Check Index #{spot_idx}:")
    print(f"  Product ID: {products[spot_idx]['id']}")
    print(f"  Title: {products[spot_idx]['title']}")
    print(f"  Vector norm: {np.linalg.norm(embeddings[spot_idx]):.4f}")

    print("\nArtifact generation and verification COMPLETE.")

if __name__ == "__main__":
    generate_and_save_artifacts()
