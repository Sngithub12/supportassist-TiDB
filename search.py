import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.db import fetchall
from src.embeddings import embed_text

# Hardcoded minimal docs for offline mode
_LOCAL_DOCS = [
    {"id": 1, "title": "Login Timeout", "content": "Check TiDB server connection and client credentials."},
    {"id": 2, "title": "Network Config", "content": "Verify firewall rules and network latency issues."},
    {"id": 3, "title": "Error 5001", "content": "Database internal error; retry or escalate."},
]
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

def vector_search(query_vec: list[float], limit: int = 5):
    try:
        sql = """
            SELECT id, title, content, embedding
            FROM docs
        """
        rows = fetchall(sql)

        docs = []
        for r in rows:
            try:
                emb = np.array(json.loads(r["embedding"]))
                score = cosine_similarity([query_vec], [emb])[0][0]
                confidence = round(score * 100, 2)  # convert to %
            except Exception:
                score = -1
                confidence = 0

            docs.append({
                "id": r["id"],
                "title": r["title"],
                "content": r["content"],
                "dist": 1 - score,
                "confidence": confidence,
                "fallback": False
            })

        # Sort by highest confidence
        docs = sorted(docs, key=lambda d: -d["confidence"])[:limit]
        return docs

    except Exception as e:
        print(f"[WARN] Vector search failed: {e} → using offline docs")
        return offline_fallback(limit)

# Try DB vector search, fallback to Python similarity


# Offline fallback (still keep sample docs as last resort)
from python_from_csv import load_from_csv

def offline_fallback(limit: int = 5):
    docs = load_from_csv("docs.csv")
    if docs:
        for r in docs[:limit]:
            r["dist"] = None
            r["fallback"] = True
        return docs[:limit]

    # Last resort: built-in minimal docs
    fallback = _LOCAL_DOCS[:limit]
    for r in fallback:
        r["dist"] = None
        r["fallback"] = True
    return fallback


# Naive keyword re-rank
def keyword_filter(rows: list[dict], text_query: str) -> list[dict]:
    text = (text_query or "").lower()

    def score(r):
        hay = f"{r.get('title','')} {r.get('content','')}".lower()
        bonus = -0.5 if text and text in hay else 0
        return bonus

    return sorted(rows, key=score)
