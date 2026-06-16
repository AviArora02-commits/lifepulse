# LifePulse Architecture

LifePulse has three layers: proactive life-event detection, reactive branch-deflection resolution, and escalation/contact. The backend exposes FastAPI routes and WebSockets. The orchestrator models a LangGraph state machine: INTAKE, CLASSIFY, ROUTE, EXECUTE, VERIFY, RESOLVE or ESCALATE, CLOSE.

The CBS integration is represented by MCP-style tools in `backend/mcp_server/server.py`. Data is JSON-backed but shaped like real CBS reads and writes: account details, UPI transactions, salary credits, product holdings, service requests, disputes, and document generation.

Every agent writes receipts and audit entries. Customers see only useful outcomes; RMs see confidence, sentiment, suggested path, and "do not say" guidance. This separation is important for banking UX: transparency for operators without making customers reason about model internals.

For production, replace the deterministic handlers with OpenAI Agents SDK workers inside the same node interfaces, back session state with Redis, persist life graph/audit data in PostgreSQL + pgvector, and send traces to LangSmith.
