"""
IntentCart - ML Subsystem
Script: 04_faiss_search.py

Objective:
1. Build an in-memory FAISS vector index (IndexFlatIP) from normalized product embeddings.
2. Search the index using natural-language queries.
3. Inspect and verify semantic retrieval results, similarity scores, and product metadata.
"""

import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def product_to_searchable_text(product: dict) -> str:
    """Converts product attributes into semantic text for embedding."""
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

def build_faiss_index(products: list, model: SentenceTransformer):
    """
    Encodes product texts with L2 normalization and indexes them in FAISS IndexFlatIP.
    """
    searchable_texts = [product_to_searchable_text(p) for p in products]
    
    # Generate L2-normalized float32 embeddings
    embeddings = model.encode(searchable_texts, normalize_embeddings=True, convert_to_numpy=True)
    embeddings = embeddings.astype(np.float32)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product on normalized vectors == Cosine Similarity
    index.add(embeddings)
    
    return index, embeddings

def search(query: str, index: faiss.Index, products: list, model: SentenceTransformer, top_k: int = 5):
    """
    Encodes a user query and searches the FAISS index for top_k most similar products.
    """
    print(f"\n==================================================================================")
    print(f"QUERY: \"{query}\"")
    print(f"==================================================================================")
    
    # 1. Encode query with L2-normalization
    query_vector = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    query_vector = query_vector.astype(np.float32)
    
    # 2. Search FAISS index
    scores, indices = index.search(query_vector, top_k)
    
    scores = scores[0]
    indices = indices[0]
    
    # 3. Display formatted tabular results
    header = f"{'Rank':<5} {'ID':<10} {'Score':<8} {'Price':<8} {'Pattern':<12} {'Material':<12} {'Season':<8} {'Style':<10} {'Title'}"
    print(header)
    print("-" * 105)
    
    for rank, (idx, score) in enumerate(zip(indices, scores), 1):
        p = products[idx]
        price_str = f"Rs.{p['price']}"
        print(f"{rank:<5} {p['id']:<10} {score:<8.4f} {price_str:<8} {p['pattern']:<12} {p['material']:<12} {p['season']:<8} {p['style']:<10} {p['title']}")
        print(f"      Occasion: {p['occasion']} | Category: {p['category']} ({p['gender']}) | Stock: {p['stock']}")
        print()

def main():
    # Load dataset
    dataset_path = os.path.join("data", "demo_products.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        products = json.load(f)
        
    print(f"Loaded {len(products)} products from {dataset_path}.")

    # Load model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading model: {model_name}...")
    model = SentenceTransformer(model_name)

    # Build index
    print("Building FAISS IndexFlatIP (Inner Product / Cosine Similarity)...")
    index, _ = build_faiss_index(products, model)
    print(f"FAISS index built successfully. Total vectors indexed: {index.ntotal}\n")

    # Primary search query (Phase 8 requirement)
    primary_query = "I need a comfortable minimal formal kurta for a summer wedding"
    search(primary_query, index, products, model, top_k=5)

    # Phase 9: Systematic verification across diverse query intents
    verification_queries = [
        "I need a breathable summer wedding kurta",
        "minimal formal kurta for a wedding",
        "casual everyday shirt",
        "traditional festive outfit",
        "comfortable clothing for hot weather"
    ]

    print("\n\n" + "#" * 80)
    print("### PHASE 9: SYSTEMATIC VERIFICATION OF DIVERSE QUERIES ###")
    print("#" * 80)

    for q in verification_queries:
        search(q, index, products, model, top_k=3)

if __name__ == "__main__":
    main()
