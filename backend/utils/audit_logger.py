from __future__ import annotations

from backend.models.schemas import AuditEntry


class AuditLogger:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def log(
        self,
        agent_id: str,
        customer_id: str,
        action_type: str,
        input_summary: str,
        output_summary: str,
        confidence: float,
        approved_by: str = "system",
    ) -> AuditEntry:
        entry = AuditEntry(
            agent_id=agent_id,
            customer_id=customer_id,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            confidence=confidence,
            approved_by=approved_by,
        )
        self.entries.append(entry)
        return entry


audit_logger = AuditLogger()
