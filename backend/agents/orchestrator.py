"""
LifePulse uses a LangGraph-style state machine because the product is not a
single prompt-response chatbot. A banking conversation has durable state,
parallel evidence gathering, consent gates, verification, conflict handling,
fallback paths, and audit requirements. A simple chain can answer "what is my
balance?", but it cannot safely coordinate a stuck UPI dispute, a simultaneous
life-event signal, an OTP-gated account action, and an RM handoff without
turning into hidden conditional logic. The graph makes those transitions
explicit: INTAKE, CLASSIFY, ROUTE, EXECUTE, VERIFY, RESOLVE or ESCALATE, and
CLOSE. Each transition is logged with confidence and action metadata, which is
what a bank needs for operational review and RBI-grade auditability.

In production this module can swap the deterministic fallback agents for
LangGraph nodes backed by OpenAI Agents SDK sub-agents. The interface remains
the same: nodes read from a shared session context bus, call MCP CBS tools,
write receipts and audit entries, and return typed messages. For the hackathon
demo, deterministic execution is intentional. It removes external API failure
as the main live-demo risk while still showing the exact orchestration pattern
that would run with real models, pgvector memory, Redis session state, and
LangSmith traces enabled.
"""

from __future__ import annotations

from backend.agents.intent_classifier import classify_intent
from backend.agents.life_event_detector import detect_life_events
from backend.agents.resolution import (
    complaint_agent,
    document_agent,
    escalation_agent,
    kyc_update_agent,
    literacy_agent,
    product_ops_agent,
    transaction_resolver,
)
from backend.memory.life_graph import life_graph
from backend.memory.session_store import session_store
from backend.models.schemas import ChatRequest, ChatResponse, Message
from backend.utils.audit_logger import audit_logger
from backend.utils.frustration_detector import score_frustration

STATE_FLOW = ["INTAKE", "CLASSIFY", "ROUTE", "EXECUTE", "VERIFY", "RESOLVE", "CLOSE"]


def _agent_for(name: str):
    return {
        "transaction_resolver": transaction_resolver.handle,
        "document_agent": document_agent.handle,
        "kyc_update_agent": kyc_update_agent.handle,
        "product_ops_agent": product_ops_agent.handle,
        "complaint_agent": complaint_agent.handle,
        "financial_literacy_agent": literacy_agent.handle,
    }.get(name, literacy_agent.handle)


def run_turn(req: ChatRequest) -> ChatResponse:
    session = session_store.get_or_create(req.customer_id, req.session_id)
    state_trace: list[str] = []

    def set_state(state: str) -> None:
        session.current_state = state
        state_trace.append(state)
        audit_logger.log("orchestrator", req.customer_id, "state_transition", req.message, state, 1.0)

    set_state("INTAKE")
    session.messages.append(Message(sender="customer", text=req.message))
    session.frustration_score = score_frustration(req.message)

    set_state("CLASSIFY")
    intent = classify_intent(req.message)
    audit_logger.log("intent_classifier", req.customer_id, intent.intent, req.message, intent.routed_agent, intent.confidence)
    if intent.clarification:
        session.messages.append(Message(sender="agent", text=intent.clarification, payload={"confidence": intent.confidence}))
        session_store.save(session)
        return ChatResponse(session=session, messages=session.messages[-2:], state_trace=state_trace, audit=audit_logger.entries[-6:])

    set_state("ROUTE")
    if intent.routed_agent == "life_event_detector" or "proactive" in req.message.lower():
        event = detect_life_events(req.customer_id)
        if event and event.confidence >= 0.75:
            life_graph.add_event(req.customer_id, event)
            messages = [
                Message(sender="agent", text="Congratulations - it looks like you may have recently welcomed a baby. Am I right?" if req.language == "en" else "Badhai ho - lagta hai aapke ghar baby aaya hai. Kya yeh sahi hai?"),
                Message(sender="system", type="recommendation", text="Life event recommendations", payload={
                    "event": event.model_dump(),
                    "why": event.evidence,
                    "confidence": event.confidence,
                    "products": [
                        {"name": "Sukanya Samriddhi Yojana", "summary": "Government-backed savings for a girl child's future."},
                        {"name": "Child Term Plan", "summary": "Protects the family if income is disrupted."},
                        {"name": "Education SIP", "summary": "Starts a small monthly investment for future education costs."},
                    ],
                }),
            ]
            receipt_confidence = event.confidence
        else:
            messages = [Message(sender="agent", text="I found a possible life-event signal and queued it for RM review instead of acting on low confidence.")]
            receipt_confidence = event.confidence if event else 0.0
        session.active_agents = ["life_event_detector"]
        audit_logger.log("life_event_detector", req.customer_id, "detect_life_event", req.message, "new_baby signal evaluated", receipt_confidence)
    elif intent.routed_agent == "escalation_agent":
        messages, receipt, confidence, brief = escalation_agent.handle(req.customer_id, req.message, session.frustration_score)
        session.rm_brief = brief
        session.sr_number = receipt.sr_number
        session.active_agents = ["escalation_agent"]
        life_graph.remember_resolution(receipt.model_dump())
        audit_logger.log("escalation_agent", req.customer_id, "warm_handoff", req.message, receipt.model_dump_json(), confidence)
    else:
        handler = _agent_for(intent.routed_agent)
        messages, receipt, confidence = handler(req.customer_id, req.message, req.language)
        session.active_agents = [intent.routed_agent]
        if receipt.sr_number:
            session.sr_number = receipt.sr_number
        life_graph.remember_resolution(receipt.model_dump())
        audit_logger.log(intent.routed_agent, req.customer_id, "resolve", req.message, receipt.model_dump_json(), confidence, "system")
        if confidence < 0.6:
            extra, esc_receipt, _, brief = escalation_agent.handle(req.customer_id, req.message, session.frustration_score)
            messages.extend(extra)
            session.rm_brief = brief
            session.sr_number = esc_receipt.sr_number

    set_state("EXECUTE")
    session.messages.extend(messages)
    set_state("VERIFY")
    set_state("RESOLVE" if not session.rm_brief else "ESCALATE")
    session.resolution_status = "escalated" if session.rm_brief else "resolved"
    set_state("CLOSE")
    session_store.save(session)
    return ChatResponse(session=session, messages=messages, state_trace=state_trace, audit=audit_logger.entries[-12:])
