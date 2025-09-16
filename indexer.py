from src.embeddings import embed_text
from src.db import execute

docs = [
    {"title": "Login Timeout", "content": "When login fails due to timeout..."},
    {"title": "Connection Refused", "content": "If the server refuses connection..."},
    {"title": "High Latency", "content": "Performance issues may cause high latency..."}
]

for d in docs:
    vec = embed_text(d["content"])  # embedding array
    execute(
        "INSERT INTO docs (title, content, embedding) VALUES (%s, %s, %s)",
        (d["title"], d["content"], vec.tolist())
    )
