import argparse, json
from pathlib import Path
from embeddings import embed_text
from db import execute

def insert_doc(title: str, content: str, doc_type: str = "kb"):
    emb = embed_text(content)
    emb_json = json.dumps(emb)
    sql = "INSERT INTO docs (doc_type, title, content, embedding) VALUES (%s,%s,%s, CAST(%s AS VECTOR(384)))"
    execute(sql, (doc_type, title, content, emb_json))

def read_text_file(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def main(path: str):
    base = Path(path)
    files = list(base.glob("**/*"))
    count = 0
    for f in files:
        if f.is_file() and f.suffix.lower() in {".txt", ".md"}:
            content = read_text_file(f)
            insert_doc(title=f.stem, content=content, doc_type="kb")
            print(f"Ingested: {f}")
            count += 1
    if count == 0:
        print("No .txt or .md files found. Add some to sample_data/ and re-run.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="sample_data")
    args = parser.parse_args()
    main(args.path)
