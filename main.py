import os
import json
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class Ticket(BaseModel):
    ticket_id: str
    channel: str | None = None
    locale: str | None = None
    message: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/sort-ticket")
def sort_ticket(ticket: Ticket):

    prompt = f"""
You are an AI support-ticket triage system.

Analyze the customer message and return ONLY valid JSON.

Customer Message:
{ticket.message}

Output format:

{{
  "case_type": "...",
  "severity": "...",
  "department": "...",
  "agent_summary": "...",
  "human_review_required": true,
  "confidence": 0.95
}}

Rules:

Case Types:
- phishing_or_social_engineering
- payment_failed
- wrong_transfer
- refund_request
- account_issue
- technical_issue
- fraud_report
- other

Severity:
- low
- medium
- high
- critical

Departments:
- fraud_risk
- payments_ops
- dispute_resolution
- customer_support
- technical_support
- account_security

human_review_required:
true if severity is high/critical or fraud related.

Return JSON only.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    ai_result = response.choices[0].message.content

    try:
        result = json.loads(ai_result)

    except Exception:
        result = {
            "case_type": "other",
            "severity": "medium",
            "department": "customer_support",
            "agent_summary": "Unable to classify ticket.",
            "human_review_required": True,
            "confidence": 0.50
        }

    return {
        "ticket_id": ticket.ticket_id,
        **result
    }