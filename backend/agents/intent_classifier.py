from __future__ import annotations

from backend.models.schemas import IntentResult
from backend.utils.frustration_detector import score_frustration

INTENTS = {
    "transaction_dispute": ("transaction_resolver", ["upi", "stuck", "failed", "refund", "reversal", "transaction"]),
    "statement_request": ("document_agent", ["statement", "visa", "pdf", "excel", "certificate"]),
    "kyc_update": ("kyc_update_agent", ["kyc", "aadhaar", "address", "nominee", "phone"]),
    "product_ops": ("product_ops_agent", ["card", "cheque", "fd", "loan", "block", "renew"]),
    "complaint": ("complaint_agent", ["complaint", "ombudsman", "not resolved"]),
    "financial_literacy": ("financial_literacy_agent", ["emi", "sip", "tax", "interest", "explain"]),
    "life_event_signal": ("life_event_detector", ["baby", "marriage", "home", "salary", "relocation", "proactive", "life event"]),
    "explicit_human_request": ("escalation_agent", ["human", "rm", "manager", "call me"]),
}


def classify_intent(message: str) -> IntentResult:
    text = message.lower()
    frustration = score_frustration(text)
    if frustration > 0.7:
        return IntentResult(intent="frustrated_escalation", confidence=0.92, routed_agent="escalation_agent", urgency_score=0.95)

    best = ("general_query", "financial_literacy_agent", 0.58)
    for intent, (agent, terms) in INTENTS.items():
        hits = sum(term in text for term in terms)
        if hits:
            best = (intent, agent, min(0.68 + hits * 0.12, 0.96))
            break

    intent, agent, confidence = best
    clarification = None if confidence >= 0.72 else "I can help. Is this about a transaction, statement, KYC, product service, or a complaint?"
    return IntentResult(intent=intent, confidence=confidence, routed_agent=agent, urgency_score=max(frustration, confidence - 0.15), clarification=clarification)
