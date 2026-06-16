from __future__ import annotations

from backend.mcp_server import server as cbs
from backend.models.schemas import AgentReceipt, Message


def handle(customer_id: str, message: str, language: str = "en") -> tuple[list[Message], AgentReceipt, float]:
    txn = next((t for t in cbs.get_transaction_history(customer_id) if t["status"] == "stuck_npci"), None)
    if not txn:
        receipt = AgentReceipt(asked=message, done=["Checked recent transactions"], account_changes=[], next_steps=["Share transaction ID if available"])
        return [Message(sender="agent", text="I could not find a stuck transaction in recent activity.")], receipt, 0.55

    dispute = cbs.file_dispute(txn["transaction_id"], "UPI stuck at NPCI")
    reversal = cbs.request_reversal(txn["transaction_id"])
    text = (
        f"I found the UPI payment of Rs {txn['amount']:,} to {txn['merchant']}. It is stuck at NPCI, "
        f"so I filed dispute {dispute['sr_number']} and queued reversal {reversal['reference']}. Expected resolution: 2 hours."
    )
    if language == "hi":
        text = f"Rahul ko Rs {txn['amount']:,} ka UPI NPCI par atka hai. Maine dispute {dispute['sr_number']} file kar diya hai. Resolution 2 ghante mein expected hai."
    receipt = AgentReceipt(
        asked=message,
        done=[f"Fetched transaction {txn['transaction_id']}", f"Filed NPCI dispute {dispute['sr_number']}", f"Queued reversal {reversal['reference']}", "Simulated SMS confirmation sent"],
        account_changes=["No debit reversal yet; reversal is queued"],
        next_steps=["Wait up to 2 hours", "Use SR number if the amount is not credited"],
        sr_number=dispute["sr_number"],
        references=[txn["transaction_id"], txn["npci_ref"], reversal["reference"]],
    )
    return [
        Message(sender="agent", text=text),
        Message(sender="system", type="action", text=f"NPCI dispute filed: {dispute['sr_number']}", payload={"status": "success"}),
        Message(sender="system", type="receipt", text="Resolution receipt generated", payload=receipt.model_dump()),
    ], receipt, 0.91
