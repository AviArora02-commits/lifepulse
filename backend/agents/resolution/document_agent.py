from __future__ import annotations

from backend.mcp_server import server as cbs
from backend.models.schemas import AgentReceipt, Message
from backend.utils.pdf_generator import generate_statement_pdf


def handle(customer_id: str, message: str, language: str = "en") -> tuple[list[Message], AgentReceipt, float]:
    customer = cbs.get_account_details(customer_id)
    doc = cbs.generate_document(customer_id, "six_month_statement", "last_6_months")
    pdf_path = generate_statement_pdf(customer["name"], customer_id)
    text = "Your 6-month bank statement for visa is ready as a digitally signed PDF. I have delivered it here and sent a copy to your registered email."
    if language == "hi":
        text = "Aapka 6 mahine ka visa bank statement digitally signed PDF ke roop mein ready hai. Maine yahan aur registered email par bhej diya hai."
    receipt = AgentReceipt(
        asked=message,
        done=[f"Generated {doc['document_id']}", "Digitally signed PDF", "Delivered to chat", "Simulated email delivery"],
        account_changes=["No account changes made"],
        next_steps=["Use the PDF for visa submission", "Ask for an ITR certificate if the embassy requests it"],
        references=[doc["document_id"], pdf_path],
    )
    return [
        Message(sender="agent", text=text),
        Message(sender="system", type="document", text="Statement ready", payload={"document_id": doc["document_id"], "path": pdf_path, "offer": "I can also generate an ITR certificate for your visa file."}),
        Message(sender="system", type="receipt", text="Resolution receipt generated", payload=receipt.model_dump()),
    ], receipt, 0.9
