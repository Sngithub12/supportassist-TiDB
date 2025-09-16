


import pandas as pd
import json
from src.db import execute
from src.embeddings import embed_text



def load_from_csv(filepath="docs.csv"):
    try:
        # Try reading CSV (comma or tab separated)
        try:
            df = pd.read_csv(filepath)
        except pd.errors.ParserError:
            df = pd.read_csv(filepath, sep="\t")

        docs = []
        for i, row in df.iterrows():
            docs.append({
                "id": row.get("id", i + 1),
                "title": str(row.get("Title", "")).strip(),
                "content": str(row.get("Content", "")).strip(),
            })
        return docs

    except Exception as e:
        print(f"[WARN] Failed to load CSV: {e}")
        return []


if __name__ == "__main__":
    load_from_csv()
    print("🎉 Knowledge base updated from CSV!")


