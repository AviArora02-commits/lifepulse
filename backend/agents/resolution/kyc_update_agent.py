from backend.models.schemas import AgentReceipt, Message


def handle(customer_id: str, message: str, language: str = "en"):
    receipt = AgentReceipt(asked=message, done=["Initiated Aadhaar OTP", "Fetched DigiLocker profile", "Queued CBS update after OTP"], account_changes=["Pending OTP approval"], next_steps=["Enter OTP 123456 to approve"])
    return [Message(sender="agent", text="I can update this with Aadhaar OTP and DigiLocker. Enter OTP 123456 in chat to approve."), Message(sender="system", type="otp", text="OTP required", payload={"purpose": "KYC update"})], receipt, 0.84
