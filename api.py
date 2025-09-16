from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from src.embeddings import embed_text
from src.search import vector_search, keyword_filter
from src.llm import summarize_with_context
from src.actions import post_to_slack, create_jira_ticket, audit_action

app = FastAPI(title="SupportAssist API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev: open CORS
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

class QueryBody(BaseModel):
    text: str
    create_action: bool = False
    action_type: Optional[str] = None  # "slack" or "jira"

@app.get("/health")
async def health():
    try:
        from src.db import fetchall
        fetchall("SELECT 1")
        return {"ok": True, "db_connected": True}
    except Exception:
        return {"ok": True, "db_connected": False}
from src.llm import summarize_with_context, set_provider

@app.post("/set_llm")
async def switch_llm(provider: str):
    ok = set_provider(provider.lower())
    return {"ok": ok, "active_provider": provider}

@app.post("/query")
async def query(body: QueryBody):
    q = body.text
    q_vec = embed_text(q)

    # Search KB
    rows = vector_search(q_vec, limit=5)
    rows = keyword_filter(rows, q)

    # Confidence score (take highest among results)
    best_conf = 0
    if rows:
        best_conf = rows[0].get("confidence", 0)

    fallback = any(r.get("fallback") for r in rows)
    answer = summarize_with_context(q, rows)

    # Handle actions (Slack/Jira)
    action_result = None
    if body.create_action and body.action_type:
        if body.action_type == "slack":
            ok, data = post_to_slack(q, answer, rows)
            action_result = {"type": "slack", "ok": ok, "data": data}
            audit_action(q, answer, "slack", action_result)

        elif body.action_type == "jira":
            title = ("SupportAssist: " + q)[:100]
            ok, data = create_jira_ticket(title=title, description=answer)
            action_result = {"type": "jira", "ok": ok, "data": data}
            audit_action(q, answer, "jira", action_result)

    return {
        "answer": answer,
        "sources": rows,
        "confidence": best_conf,
        "action_result": action_result,
        "fallback": fallback
    }
