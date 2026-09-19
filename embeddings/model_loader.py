from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_cached_model = None

def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """
    Returns a cached SentenceTransformer instance to avoid redundant reloading.
    """
    global _cached_model
    if _cached_model is None:
        print(f"Loading embedding model [{model_name}] on CPU...")
        _cached_model = SentenceTransformer(model_name)
        print("Embedding model ready.")
    return _cached_model
