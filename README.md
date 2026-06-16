# LifePulse

LifePulse is a hackathon-ready agentic banking demo with a FastAPI backend, LangGraph-style orchestrator, deterministic resolution agents, realistic Indian CBS mock data, WebSocket-ready routes, and a React customer/RM interface.

## Run in 3 commands

```bash
cd lifepulse
docker compose up --build
```

Open:

- Customer chat + demo landing: `http://localhost:5173`
- API health: `http://localhost:8000`
- Live metrics: `http://localhost:8000/api/metrics/live`

## Demo flows

- Stuck UPI: `My UPI of Rs 8,500 to Rahul is stuck since yesterday`
- Visa statement: `Need 6 month bank statement for visa application`
- Frustrated customer: `I've been waiting 3 days this is ridiculous`
- Life event: click `Life event`

## Production controls represented

- OTP gates for account-changing actions
- Confidence thresholds and RM review handoff
- Immutable in-memory audit log surfaced on the RM dashboard
- Rule-based fallback behavior for top demo intents
- Proactive life-event scan endpoint and APScheduler job
- LangSmith environment variables included for tracing in a real deployment

External LLM calls are intentionally not required for the live demo, so judging does not depend on network, API quota, or model latency.
