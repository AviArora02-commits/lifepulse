from __future__ import annotations

from backend.mcp_server import server as cbs
from backend.models.schemas import AgentReceipt, Message, RMBrief


def build_rm_brief(customer_id: str, issue: str, attempts: list[str], sentiment: float) -> RMBrief:
    customer = cbs.get_account_details(customer_id)
    products = cbs.get_product_holdings(customer_id)
    return RMBrief(
        customer_snapshot={
            "name": customer["name"],
            "tenure_years": customer["tenure_years"],
            "product_count": len(products),
            "ltv_segment": customer["ltv_segment"],
            "masked_phone": customer["phone"],
        },
        issue_summary=f"Customer is frustrated about: {issue[:140]}. They need acknowledgement, ownership, and a clear time commitment.",
        attempts_made=attempts or ["Frustration detected before account action; RM brief prepared immediately"],
        do_not_say=["Please visit the branch", "Repeat the full issue again", "It is only a system delay"],
        recommended_resolution="Take ownership, confirm SR, offer callback or immediate RM chat, and commit to a 6-hour update.",
        sentiment_score=sentiment,
        frustration_trigger=issue,
        pre_approved_waiver=750.0 if customer["ltv_segment"] in {"high", "premium"} else 250.0,
    )


def handle(customer_id: str, message: str, sentiment: float) -> tuple[list[Message], AgentReceipt, float, RMBrief]:
    sr = cbs.create_service_request(customer_id, "priority_escalation", message)
    brief = build_rm_brief(customer_id, message, ["Priority service request created"], sentiment)
    receipt = AgentReceipt(
        asked=message,
        done=[f"Created priority SR {sr['sr_number']}", "Prepared RM brief", "Notified RM dashboard"],
        account_changes=["No account debit or product change"],
        next_steps=["Connect now", "Schedule callback", "Receive 6-hour update"],
        sr_number=sr["sr_number"],
    )
    return [
        Message(sender="agent", text="I am sorry you have had to wait. I am taking ownership now and preparing a human handoff with the full context, so you do not need to repeat yourself."),
        Message(sender="system", type="escalation", text=f"Priority SR created: {sr['sr_number']}", payload={"brief": brief.model_dump(), "choices": ["Connect now", "Schedule callback", "Raise complaint"]}),
        Message(sender="system", type="receipt", text="Escalation receipt generated", payload=receipt.model_dump()),
    ], receipt, 0.88, brief
