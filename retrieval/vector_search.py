"""
IntentCart - ML Subsystem
Module: retrieval/vector_search.py

Objective (Phase 17):
Vector search candidate retriever.
Loads the persisted FAISS index and metadata artifacts, encodes the user query,
and retrieves the Top-K (default 30) candidate products based on cosine similarity.
"""

import json
import os
import sys
import numpy as np
import faiss

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from embeddings.model_loader import get_embedding_model

class VectorSearchRetriever:
    """
    Manages FAISS index loading and vector retrieval.
    Guarantees that FAISS integer indices map 1-to-1 with product metadata.
    """

    def __init__(self, index_path: str = None, metadata_path: str = None):
        self.index_path = index_path or config.FAISS_INDEX_PATH
        self.metadata_path = metadata_path or config.METADATA_PATH
        self.index = None
        self.metadata = None
        self.model = None
        self._load_artifacts()

    def _load_artifacts(self):
        """Loads FAISS index binary and metadata JSON from disk."""
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"FAISS index not found at '{self.index_path}'. "
                f"Please run 'python embeddings/generate_embeddings.py' first to build the index."
            )
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(
                f"Product metadata not found at '{self.metadata_path}'. "
                f"Please run 'python embeddings/generate_embeddings.py' first."
            )

        print(f"Loading FAISS index from: {self.index_path}...")
        self.index = faiss.read_index(self.index_path)

        print(f"Loading product metadata from: {self.metadata_path}...")
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        # Enforce 1-to-1 alignment invariant
        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                f"Index/Metadata length mismatch: FAISS has {self.index.ntotal} vectors, "
                f"but metadata has {len(self.metadata)} items."
            )

        self.model = get_embedding_model()
        print(f"Vector search ready. Indexed items: {self.index.ntotal}")

    def retrieve_candidates(
        self,
        query: str,
        top_k: int = config.RETRIEVAL_K
    ) -> list[tuple[dict, float]]:
        """
        Retrieves top_k candidates most semantically similar to the query.
        Returns:
            List of tuples: [(product_metadata_dict, cosine_similarity_float), ...]
        """
        if not query or not query.strip():
            return []

        # 1. Encode and normalize query
        query_vector = self.model.encode(
            [query.strip()],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype(np.float32)

        # Clamp k to total indexed items
        k = min(top_k, self.index.ntotal)

        # 2. Search FAISS index
        scores, indices = self.index.search(query_vector, k)
        scores = scores[0]
        indices = indices[0]

        # 3. Assemble candidate pairs with exact 1-to-1 metadata lookup
        candidates = []
        for idx, score in zip(indices, scores):
            if idx < 0 or idx >= len(self.metadata):
                continue
            product = self.metadata[idx]
            candidates.append((product, float(score)))

        return candidates


def _run_self_tests():
    """Verifies vector retrieval against persisted artifacts."""
    print("Running VectorSearchRetriever Self-Tests...")
    retriever = VectorSearchRetriever()
    test_query = "comfortable minimal summer wedding kurta"
    candidates = retriever.retrieve_candidates(test_query, top_k=5)

    print(f"\nQuery: '{test_query}'")
    print(f"Retrieved {len(candidates)} candidates:")
    for rank, (prod, sim) in enumerate(candidates, 1):
        print(f"  #{rank} [Sim={sim:.4f}] Rs.{prod.get('price')} | {prod.get('title')}")

    assert len(candidates) == 5
    assert candidates[0][1] >= candidates[1][1] >= candidates[2][1]
    print("\nVectorSearchRetriever self-test PASSED successfully.")

if __name__ == "__main__":
    _run_self_tests()
