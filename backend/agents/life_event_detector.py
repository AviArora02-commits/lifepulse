from __future__ import annotations

from backend.mcp_server import server as cbs
from backend.models.schemas import LifeEvent


def detect_life_events(customer_id: str) -> LifeEvent | None:
    categories = cbs.get_spending_categories(customer_id)
    products = cbs.get_product_holdings(customer_id)
    navigation = cbs.get_app_navigation_events(customer_id)
    evidence = []

    if categories.get("baby_care", 0) >= 2:
        evidence.append("Repeated baby-care purchases over the last 3 months")
    if any(p.get("nominee") for p in products):
        evidence.append("Spouse recently appears as FD nominee")
    if any(e["screen"] == "child_plan_calculator" and e["count"] >= 2 for e in navigation):
        evidence.append("Customer browsed child-plan calculator twice")

    if len(evidence) >= 3:
        return LifeEvent(
            event_type="new_baby",
            confidence=0.87,
            evidence=evidence,
            products_triggered=["Sukanya Samriddhi Yojana", "Child Term Plan", "Education SIP"],
            outcome="pitched",
        )
    if evidence:
        return LifeEvent(event_type="new_baby", confidence=0.64, evidence=evidence, products_triggered=[], outcome="pending")
    return None


LIFE_EVENT_TAXONOMY = [
    "marriage",
    "home_purchase",
    "new_baby",
    "salary_jump",
    "job_change",
    "relocation",
    "retirement_approaching",
    "first_salary",
    "nri_status",
    "vehicle_purchase",
    "education_loan_signal",
    "medical_emergency",
]
