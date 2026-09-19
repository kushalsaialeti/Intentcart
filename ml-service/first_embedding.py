"""
IntentCart - ML Subsystem
Script: 01_first_embedding.py

Objective:
Demonstrate loading a pretrained Sentence Transformer model and generating
dense vector embeddings from natural-language sentences.
"""

from sentence_transformers import SentenceTransformer

def main():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading pretrained model: {model_name}...")
    model = SentenceTransformer(model_name)
    print("Model loaded successfully.\n")

    # Sample domain-relevant sentences for IntentCart
    sentences = [
        "comfortable minimal summer wedding kurta",
        "breathable formal men's kurta for a wedding",
        "floral printed casual shirt"
    ]

    print(f"Input sentences ({len(sentences)} items):")
    for i, s in enumerate(sentences, 1):
        print(f"  {i}. \"{s}\"")
    print()

    print("Generating embeddings...")
    embeddings = model.encode(sentences)

    print("\n--- Embedding Verification ---")
    print(f"Embeddings type: {type(embeddings)}")
    print(f"Embeddings array shape: {embeddings.shape}")
    print(f"Total sentences: {embeddings.shape[0]}")
    print(f"Embedding dimension per sentence: {embeddings.shape[1]}")

    # Inspect the first sentence's vector: show first 5 components and total norm
    first_vector = embeddings[0]
    print(f"\nFirst vector preview (first 5 of {len(first_vector)} dimensions):")
    print(f"  {first_vector[:5]}")
    print(f"  ... (379 remaining float values omitted for readability)")

if __name__ == "__main__":
    main()
