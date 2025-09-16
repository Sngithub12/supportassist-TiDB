import json
import requests
from src.config import settings
from src.db import execute
from requests.auth import HTTPBasicAuth


def audit_action(query_text: str, response: str, action_type: str, payload: dict):
    """Save all Slack/Jira actions to TiDB for audit logging."""
    sql = """
    INSERT INTO actions_audit (query_text, response, action_type, action_payload)
    VALUES (%s, %s, %s, %s)
    """
    execute(sql, (query_text, response, action_type, json.dumps(payload)))


def post_to_slack(question: str, answer: str, sources=None) -> tuple[bool, dict]:
    url = settings.SLACK_WEBHOOK
    if not url:
        return False, {"error": "⚠️ No Slack webhook URL configured"}

    # Format sources
    sources_text = ""
    if sources:
        bullets = [f"• {row.get('title', 'Untitled')}" for row in sources]
        sources_text = "\n".join(bullets)

    # Block Kit payload
    payload_blocks = {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*💡 SupportAssist Suggestion*"}
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Question:*\n{question}\n\n*Answer:*\n{answer}"}
            },
        ]
    }

    if sources_text:
        payload_blocks["blocks"].append(
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"*Sources:*\n{sources_text}"}]
            }
        )

    # Send Block Kit first
    r = requests.post(url, json=payload_blocks)
    if r.status_code == 200:
        return True, {"status": "ok", "message": "Sent with Block Kit"}

    # Fallback: plain text
    fallback_payload = {
        "text": f"💡 SupportAssist\n\nQuestion: {question}\n\nAnswer: {answer}"
    }
    r = requests.post(url, json=fallback_payload)
    if r.status_code == 200:
        return True, {"status": "ok", "message": "Sent with plain text"}
    else:
        return False, {"status": r.status_code, "error": r.text}



def create_jira_ticket(title: str, description: str) -> tuple[bool, dict]:
    """
    Create a Jira issue via REST API using Atlassian Document Format (ADF).
    """
    url = f"{settings.JIRA_BASE_URL}/rest/api/3/issue"
    auth = HTTPBasicAuth(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    # Minimal valid ADF description
    adf_description = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": str(description)}
                ]
            }
        ]
    }

    payload = {
        "fields": {
            "project": {"key": settings.JIRA_PROJECT_KEY},
            "summary": title[:240],
            "description": adf_description,
            "issuetype": {"name": "Task"}
        }
    }

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    try:
        r = requests.post(url, json=payload, headers=headers, auth=auth)
        print("📤 Sending to Jira:", json.dumps(payload, indent=2))
        print("➡️ Status:", r.status_code)
        print("➡️ Response:", r.text)

        if r.status_code == 201:
            return True, r.json()
        else:
            return False, {"status": r.status_code, "error": r.text}
    except Exception as e:
        print("❌ Jira request failed:", e)
        return False, {"error": str(e)}
