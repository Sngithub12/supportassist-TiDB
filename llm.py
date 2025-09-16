import requests
import google.generativeai as genai
from openai import OpenAI
from src.config import settings

# Track active provider at runtime
active_provider = settings.LLM_PROVIDER.lower()

# Clients
openai_client = None
if settings.OPENAI_API_KEY:
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def set_provider(provider: str):
    """Switch active LLM provider at runtime."""
    global active_provider
    if provider in ["openai", "gemini", "ollama"]:
        active_provider = provider
        return True
    return False

def summarize_with_context(query: str, docs: list[dict]) -> str:
    context = "\n\n".join([f"{d['title']}: {d['content']}" for d in docs])
    prompt = f"""
You are SupportAssist, a troubleshooting assistant.

User query: "{query}"

Knowledge base entries:
{context}

Task: Draft a structured support response.

Summary: <short summary>
Recommended Action: <steps>
Ticket Title: <short descriptive title>
"""

    provider = active_provider

    # OpenAI
    if provider == "openai" and openai_client:
        try:
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise support assistant for TiDB."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ OpenAI error: {e}"

    # Gemini
    elif provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"⚠️ Gemini error: {e}"

    # Ollama
    elif provider == "ollama":
        try:
            resp = requests.post(f"{settings.OLLAMA_HOST}/api/generate", json={
                "model": "llama2",
                "prompt": prompt
            }, stream=False)
            return resp.json().get("response", "").strip()
        except Exception as e:
            return f"⚠️ Ollama error: {e}"

    return "⚠️ No valid LLM provider configured."
