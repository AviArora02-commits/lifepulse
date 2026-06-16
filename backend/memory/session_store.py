from __future__ import annotations

from backend.models.schemas import ConversationSession


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    def get_or_create(self, customer_id: str, session_id: str | None = None) -> ConversationSession:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        session = ConversationSession(customer_id=customer_id)
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> ConversationSession | None:
        return self._sessions.get(session_id)

    def save(self, session: ConversationSession) -> None:
        self._sessions[session.session_id] = session


session_store = SessionStore()
