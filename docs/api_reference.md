# API Reference

- `POST /api/chat/message` sends a customer message and returns session state, messages, state trace, and audit entries.
- `GET /api/chat/session/{id}` returns session history.
- `POST /api/escalate` manually triggers warm handoff.
- `GET /api/sr/{sr_id}/status` returns service request status.
- `POST /api/otp/verify` verifies demo OTP `123456`.
- `GET /api/metrics/live` returns RM dashboard metrics.
- `GET /api/audit` returns action audit entries.
- `GET /api/proactive/{customer_id}` returns proactive WhatsApp ping eligibility.
- `WS /ws/chat/{session_id}` streams chat tokens and message events.
- `WS /ws/rm-dashboard` streams metrics and recent audit rows.
