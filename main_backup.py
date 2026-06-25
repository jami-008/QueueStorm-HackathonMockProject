from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


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

    msg = ticket.message.lower()

    case_type = "other"
    severity = "low"
    department = "customer_support"
    confidence = 0.60

    # Phishing / Social Engineering
    if any(word in msg for word in [
        "otp",
        "pin",
        "password",
        "scam",
        "fraud",
        "phishing",
        "verification code"
    ]):
        case_type = "phishing_or_social_engineering"
        severity = "critical"
        department = "fraud_risk"
        confidence = 0.95

    # Wrong Transfer
    elif any(word in msg for word in [
        "wrong number",
        "wrong recipient",
        "wrong account",
        "mistaken transfer",
        "sent money to wrong",
        "sent cash to wrong"
    ]):
        case_type = "wrong_transfer"
        severity = "high"
        department = "dispute_resolution"
        confidence = 0.90

    # Payment Failed
    elif any(word in msg for word in [
        "payment failed",
        "transaction failed",
        "failed payment",
        "balance deducted"
    ]):
        case_type = "payment_failed"
        severity = "high"
        department = "payments_ops"
        confidence = 0.90

    # Refund Request
    elif any(word in msg for word in [
        "refund",
        "money back",
        "return payment"
    ]):
        case_type = "refund_request"
        severity = "low"
        department = "customer_support"
        confidence = 0.85

    # Agent Summary
    if case_type == "wrong_transfer":
        summary = "Customer sent money to the wrong recipient."

    elif case_type == "payment_failed":
        summary = "Customer reports a failed payment with possible balance deduction."

    elif case_type == "refund_request":
        summary = "Customer is requesting a refund."

    elif case_type == "phishing_or_social_engineering":
        summary = "Customer reports a possible phishing or social engineering attempt."

    else:
        summary = "Customer reported a support issue."

    return {
        "ticket_id": ticket.ticket_id,
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": summary,
        "human_review_required": (
            severity == "critical"
            or case_type == "phishing_or_social_engineering"
        ),
        "confidence": confidence
    }