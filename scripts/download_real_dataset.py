"""
IntentCart - ML Subsystem
Script: scripts/download_real_dataset.py

Objective:
Download a representative sample of real Myntra Fashion Products (~800 items)
from the standard open-source Myntra dataset repository into data/raw/.
"""

import os
import urllib.request
import pandas as pd

def main():
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "myntra_raw_sample.csv")

    source_url = "https://huggingface.co/datasets/Gssmc/myntra_dataset/resolve/main/train.csv"
    print(f"Fetching real fashion dataset sample from: {source_url}...")
    
    # We sample ~1000 rows to ensure ~600-800 valid unique clothing items after cleaning
    df_raw = pd.read_csv(source_url, nrows=1000)
    df_raw.to_csv(raw_file, index=False)
    
    print(f"Raw dataset successfully saved to: {raw_file}")
    print(f"Total rows: {len(df_raw)}")
    print(f"Columns ({len(df_raw.columns)}): {list(df_raw.columns)}")

if __name__ == "__main__":
    main()
