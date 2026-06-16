from backend.models.schemas import AgentReceipt, Message


def handle(customer_id: str, message: str, language: str = "en"):
    receipt = AgentReceipt(asked=message, done=["Identified product service request", "OTP gate prepared"], account_changes=["No changes until OTP"], next_steps=["Enter OTP 123456 to continue"])
    return [Message(sender="agent", text="I can do this, but bank policy requires OTP before any product action."), Message(sender="system", type="otp", text="OTP required", payload={"purpose": "Product operation"})], receipt, 0.82
