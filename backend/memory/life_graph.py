from __future__ import annotations

from backend.models.schemas import LifeEvent


class LifeGraph:
    def __init__(self) -> None:
        self._events: dict[str, list[LifeEvent]] = {}
        self._resolution_memory: list[dict] = []

    def add_event(self, customer_id: str, event: LifeEvent) -> None:
        self._events.setdefault(customer_id, []).append(event)

    def events_for(self, customer_id: str) -> list[LifeEvent]:
        return self._events.get(customer_id, [])

    def remember_resolution(self, receipt: dict) -> None:
        self._resolution_memory.append(receipt)

    def similar_resolutions(self, text: str) -> list[dict]:
        terms = set(text.lower().split())
        ranked = [
            r for r in self._resolution_memory
            if terms.intersection(" ".join(map(str, r.values())).lower().split())
        ]
        return ranked[-3:]


life_graph = LifeGraph()
