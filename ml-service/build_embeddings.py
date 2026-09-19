"""
IntentCart - ML Subsystem
Script: 03_build_embeddings.py

Objective:
1. Define a product representation function that converts structured product
   metadata into rich, searchable natural-language text.
2. Generate dense vector embeddings for all products using all-MiniLM-L6-v2.
3. L2-normalize the embeddings and ensure float32 format for FAISS compatibility.
"""

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

def product_to_searchable_text(product: dict) -> str:
    """
    Converts structured product metadata into a semantically dense,
    searchable text string suitable for transformer embedding.
    
    Fields that matter for semantic retrieval are included:
    title, description, category, subcategory, gender, pattern,
    material, color, season, style, occasion.

    Operational / deterministic fields (id, price, stock, rating, image_url)
    are omitted because they are handled by hard filters and post-scoring.
    """
    parts = [
        f"Product: {product.get('title', '')}",
        f"Description: {product.get('description', '')}",
        f"Category: {product.get('gender', '')} {product.get('category', '')} - {product.get('subcategory', '')}",
        f"Material: {product.get('material', '')}",
        f"Pattern: {product.get('pattern', '')}",
        f"Color: {product.get('color', '')}",
        f"Season: {product.get('season', '')}",
        f"Style: {product.get('style', '')}",
        f"Occasion: {product.get('occasion', '')}"
    ]
    return " | ".join(parts)

def main():
    # 1. Load controlled demo product dataset
    dataset_path = os.path.join("data", "demo_products.json")
    print(f"Loading dataset from: {dataset_path}...")
    with open(dataset_path, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"Loaded {len(products)} products.\n")

    # 2. Convert products into searchable text
    searchable_texts = []
    for p in products:
        text = product_to_searchable_text(p)
        searchable_texts.append(text)

    # Display preview of the first product's representation
    print("--- Sample Searchable Text Representation (Product 1) ---")
    print(searchable_texts[0])
    print("-" * 60 + "\n")

    # 3. Load Sentence Transformer model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    print("Model ready.\n")

    # 4. Generate embeddings with L2-normalization
    # normalize_embeddings=True ensures every vector has Euclidean norm ||v|| = 1.0
    print("Generating normalized product embeddings...")
    embeddings = model.encode(
        searchable_texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    # 5. Ensure float32 dtype for FAISS
    embeddings = embeddings.astype(np.float32)

    # 6. Verification
    print("\n--- Product Embedding Verification ---")
    print(f"Number of products: {len(products)}")
    print(f"Embedding matrix shape: {embeddings.shape}")
    print(f"Embedding dimensions per product: {embeddings.shape[1]}")
    print(f"Data type: {embeddings.dtype}")
    
    # Verify L2 normalization: Euclidean norm of each vector must be ~1.0
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"Vector L2 norms (min, max): ({norms.min():.4f}, {norms.max():.4f}) -> Confirms unit length")

    # Preview first vector
    print(f"\nFirst product vector preview (first 5 values): {embeddings[0][:5]}")

if __name__ == "__main__":
    main()
