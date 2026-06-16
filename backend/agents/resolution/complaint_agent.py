from backend.agents.resolution.escalation_agent import handle as escalate


def handle(customer_id: str, message: str, language: str = "en"):
    return escalate(customer_id, message, 0.76)[:3]
