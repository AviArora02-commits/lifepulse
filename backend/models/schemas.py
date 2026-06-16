from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class LifeEvent(BaseModel):
    event_type: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float
    evidence: list[str]
    products_triggered: list[str]
    outcome: Literal["pitched", "accepted", "declined", "pending"] = "pending"


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    phone: str
    account_type: str
    balance: float
    tenure_years: int
    products: list[str]
    kyc_status: str
    life_events: list[LifeEvent] = Field(default_factory=list)
    ltv_segment: Literal["low", "medium", "high", "premium"]


class Message(BaseModel):
    sender: Literal["customer", "agent", "system", "rm"]
    text: str
    type: str = "text"
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RMBrief(BaseModel):
    customer_snapshot: dict[str, Any]
    issue_summary: str
    attempts_made: list[str]
    do_not_say: list[str]
    recommended_resolution: str
    sentiment_score: float
    frustration_trigger: str
    pre_approved_waiver: float


class ConversationSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"sess_{uuid4().hex[:10]}")
    customer_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    current_state: str = "INTAKE"
    messages: list[Message] = Field(default_factory=list)
    active_agents: list[str] = Field(default_factory=list)
    frustration_score: float = 0
    resolution_status: str = "open"
    sr_number: str | None = None
    rm_brief: RMBrief | None = None


class IntentResult(BaseModel):
    intent: str
    confidence: float
    routed_agent: str
    urgency_score: float
    clarification: str | None = None


class AgentReceipt(BaseModel):
    asked: str
    done: list[str]
    account_changes: list[str]
    next_steps: list[str]
    sr_number: str | None = None
    references: list[str] = Field(default_factory=list)


class AuditEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    customer_id: str
    action_type: str
    input_summary: str
    output_summary: str
    confidence: float
    approved_by: str


class ChatRequest(BaseModel):
    session_id: str | None = None
    customer_id: str = "CUST1001"
    message: str
    language: Literal["en", "hi"] = "en"
    simple_mode: bool = False


class ChatResponse(BaseModel):
    session: ConversationSession
    messages: list[Message]
    state_trace: list[str]
    audit: list[AuditEntry]
