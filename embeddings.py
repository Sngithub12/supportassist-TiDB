
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    """Return embedding vector as plain list of floats."""
    vec = _model.encode([text])[0]   # returns numpy array
    return vec.tolist()              # convert to Python list of floats
