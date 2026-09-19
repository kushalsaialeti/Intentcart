import os
import gc

# Crucial for 512MB RAM cloud environments (Render Free Tier):
# Prevent PyTorch & numerical libraries from spawning multi-core thread pools
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
try:
    torch.set_num_interop_threads(1)
except Exception:
    pass
torch.set_num_threads(1)

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_cached_model = None

def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """
    Returns a cached SentenceTransformer instance to avoid redundant reloading.
    Optimized for low-memory CPU environments (Render 512MB free tier).
    """
    global _cached_model
    if _cached_model is None:
        print(f"Loading embedding model [{model_name}] on CPU (1 thread, low RAM mode)...")
        with torch.inference_mode():
            _cached_model = SentenceTransformer(model_name, device="cpu")
        gc.collect()
        print("Embedding model ready.")
    return _cached_model

