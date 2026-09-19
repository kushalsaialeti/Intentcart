"""
IntentCart - ML Subsystem
Configuration Module: config.py
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

# Artifact filepaths
EMBEDDINGS_PATH = os.path.join(ARTIFACTS_DIR, "product_embeddings.npy")
FAISS_INDEX_PATH = os.path.join(ARTIFACTS_DIR, "product_index.faiss")
METADATA_PATH = os.path.join(ARTIFACTS_DIR, "product_metadata.json")
CLEAN_DATA_PATH = os.path.join(DATA_DIR, "processed", "clean_products.json")
DEMO_DATA_PATH = os.path.join(DATA_DIR, "demo_products.json")

# Model Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Candidate Retrieval Configuration
RETRIEVAL_K = 30     # Number of candidates initially retrieved from vector index
FINAL_K = 5          # Number of ranked products presented in final results

# Hybrid Ranking Weights (Must sum to 1.0)
SCORING_WEIGHTS = {
    "semantic": 0.50,     # Semantic cosine similarity from vector search (50%)
    "preference": 0.20,   # Soft preference alignment: minimal, comfortable, breathable (20%)
    "occasion": 0.15,     # Event suitability: wedding, formal, festive (15%)
    "season": 0.10,       # Climate/comfort fit: summer, cotton, linen (10%)
    "rating": 0.05        # Customer satisfaction score normalized (5%)
}

# Verify weights sum to 1.0
assert abs(sum(SCORING_WEIGHTS.values()) - 1.0) < 1e-6, "Scoring weights must sum to 1.0"
