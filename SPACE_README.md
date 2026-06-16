---
title: LifePulse
emoji: ⚡
colorFrom: teal
colorTo: green
sdk: docker
pinned: false
license: mit
---

# LifePulse

Agentic banking command layer for proactive life-event detection, branch deflection, and RM warm handoff.

The Space runs a single Docker container:

- FastAPI backend on port 7860
- React/Vite frontend served from the FastAPI static mount
- Deterministic demo agents and JSON-backed CBS mock tools
- Four working demo scenarios: stuck UPI, visa statement, frustrated handoff, and life-event detection

No external LLM key is required for the demo.
