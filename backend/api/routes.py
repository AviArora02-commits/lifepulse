from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.agents.life_event_detector import detect_life_events
from backend.agents.orchestrator import run_turn
from backend.mcp_server import server as cbs
from backend.memory.session_store import session_store
from backend.models.schemas import ChatRequest
from backend.utils.audit_logger import audit_logger

router = APIRouter()


@router.post("/api/chat/message")
def chat_message(req: ChatRequest):
    return run_turn(req)


@router.get("/api/chat/session/{session_id}")
def chat_session(session_id: str):
    return session_store.get(session_id) or {"error": "session_not_found"}


@router.post("/api/escalate")
def escalate(req: ChatRequest):
    req.message = f"human requested: {req.message}"
    return run_turn(req)


@router.get("/api/sr/{sr_id}/status")
def sr_status(sr_id: str):
    return {"sr_id": sr_id, "status": "priority_open", "next_update": "within 6 hours"}


@router.post("/api/otp/verify")
def otp_verify(payload: dict):
    return {"verified": payload.get("otp") == "123456", "approved_by": "OTP"}


@router.get("/api/metrics/live")
def live_metrics():
    deflection = cbs.calculate_branch_visit_deflection()
    return {
        "conversations_today": 342,
        "avg_resolution_time": "4 minutes",
        "branch_visits_deflected": deflection["today"],
        "resolved": 286,
        "escalated": 31,
        "pending": 25,
        "competitor": "Average bank resolution time: 3-5 days | LifePulse: 4 minutes",
        "audit_entries": len(audit_logger.entries),
    }


@router.get("/api/audit")
def audit():
    return audit_logger.entries


@router.get("/api/proactive/{customer_id}")
def proactive(customer_id: str):
    event = detect_life_events(customer_id)
    if event and event.confidence > 0.8:
        return {"send": True, "message": "Hi Priya, we noticed something that might be relevant to you - want to talk?", "event": event}
    return {"send": False}


@router.websocket("/ws/chat/{session_id}")
async def chat_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            req = ChatRequest(**json.loads(raw), session_id=session_id)
            result = run_turn(req)
            for message in result.messages:
                for token in message.text.split():
                    await websocket.send_text(json.dumps({"type": "token", "token": token + " ", "state": result.session.current_state}))
                    await asyncio.sleep(0.025)
                await websocket.send_text(message.model_dump_json())
    except WebSocketDisconnect:
        return


@router.websocket("/ws/rm-dashboard")
async def rm_dashboard_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({"at": datetime.utcnow().isoformat(), "metrics": live_metrics(), "audit": [e.model_dump() for e in audit_logger.entries[-5:]]})
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        return
