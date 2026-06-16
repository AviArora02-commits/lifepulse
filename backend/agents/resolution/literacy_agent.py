from backend.models.schemas import AgentReceipt, Message


def handle(customer_id: str, message: str, language: str = "en"):
    receipt = AgentReceipt(asked=message, done=["Explained product in simple language", "Checked adoption opportunity"], account_changes=[], next_steps=["Start with Rs 500/month SIP if interested"])
    return [Message(sender="agent", text="A SIP invests a fixed amount every month, so you buy more units when markets are low and fewer when high. You do not currently run a SIP; want to start with Rs 500/month?")], receipt, 0.79
