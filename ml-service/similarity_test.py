"""
IntentCart - ML Subsystem
Script: 02_similarity_test.py

Objective:
Calculate and inspect pairwise cosine similarity between sentence embeddings
to demonstrate how semantic relatedness is quantified.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def main():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading model: {model_name}...")
    model = SentenceTransformer(model_name)

    sentences = [
        "comfortable minimal summer wedding kurta",      # Sentence A
        "breathable formal men's kurta for a wedding",   # Sentence B
        "floral printed casual shirt"                    # Sentence C
    ]

    print("\nEncoding sentences into embeddings...")
    embeddings = model.encode(sentences)

    # Compute pairwise cosine similarity matrix (3x3)
    similarity_matrix = cosine_similarity(embeddings)

    print("\n--- Cosine Similarity Matrix (3x3) ---")
    labels = ["A: Summer Kurta", "B: Formal Kurta", "C: Casual Shirt"]
    
    # Print formatted matrix
    header = f"{'':<20}" + "".join([f"{lbl:>18}" for lbl in labels])
    print(header)
    print("-" * len(header))
    for i, row_lbl in enumerate(labels):
        row_vals = "".join([f"{similarity_matrix[i][j]:>18.4f}" for j in range(len(labels))])
        print(f"{row_lbl:<20}{row_vals}")

    print("\n--- Pairwise Comparisons ---")
    print(f"Sim(A, A) [Self-similarity]:                {similarity_matrix[0][0]:.4f}")
    print(f"Sim(A, B) [Summer Kurta vs Formal Kurta]:   {similarity_matrix[0][1]:.4f}")
    print(f"Sim(A, C) [Summer Kurta vs Casual Shirt]:   {similarity_matrix[0][2]:.4f}")
    print(f"Sim(B, C) [Formal Kurta vs Casual Shirt]:   {similarity_matrix[1][2]:.4f}")

if __name__ == "__main__":
    main()
