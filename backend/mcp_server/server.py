from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from uuid import uuid4

DATA_DIR = Path(__file__).parent / "cbs_mock"


def _load(name: str) -> list[dict]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def get_account_details(customer_id: str) -> dict:
    return next(c for c in _load("customers.json") if c["customer_id"] == customer_id)


def get_transaction_history(customer_id: str, days: int = 180) -> list[dict]:
    return [t for t in _load("transactions.json") if t["customer_id"] == customer_id]


def get_product_holdings(customer_id: str) -> list[dict]:
    return [p for p in _load("products.json") if p["customer_id"] == customer_id]


def get_kyc_status(customer_id: str) -> dict:
    c = get_account_details(customer_id)
    return {"customer_id": customer_id, "status": c["kyc_status"], "last_updated": "2026-04-12"}


def get_salary_credits(customer_id: str, months: int = 6) -> list[dict]:
    return [t for t in get_transaction_history(customer_id) if t.get("category") == "salary"]


def get_transaction_status(transaction_id: str) -> dict:
    return next(t for t in _load("transactions.json") if t["transaction_id"] == transaction_id)


def get_spending_categories(customer_id: str, months: int = 6) -> dict:
    categories = Counter(t.get("category", "transfer") for t in get_transaction_history(customer_id))
    return dict(categories)


def get_app_navigation_events(customer_id: str, days: int = 90) -> list[dict]:
    return [
        {"screen": "nominee_update", "count": 3, "last_seen": "2026-05-09"},
        {"screen": "child_plan_calculator", "count": 2, "last_seen": "2026-06-10"},
        {"screen": "statement_download", "count": 1, "last_seen": "2026-06-12"},
    ]


def get_peer_benchmark(customer_id: str) -> dict:
    return {"avg_resolution_days": "3-5 days", "lifepulse_p50_minutes": 4}


def calculate_branch_visit_deflection() -> dict:
    minute = datetime.utcnow().minute
    return {"today": 118 + minute, "monthly_savings_inr": 424000 + minute * 850}


def file_dispute(transaction_id: str, reason: str) -> dict:
    return {"sr_number": f"SR{datetime.utcnow():%y%m%d}{uuid4().hex[:4].upper()}", "transaction_id": transaction_id, "reason": reason, "sla": "2 hours"}


def request_reversal(transaction_id: str) -> dict:
    return {"reference": f"REV-{uuid4().hex[:8].upper()}", "status": "queued", "eta": "2 hours"}


def get_refund_timeline(transaction_id: str) -> dict:
    return {"transaction_id": transaction_id, "customer_message": "Reversal expected within 2 hours after NPCI confirmation."}


def generate_document(customer_id: str, doc_type: str, date_range: str) -> dict:
    return {"document_id": f"DOC-{uuid4().hex[:6].upper()}", "doc_type": doc_type, "date_range": date_range}


def create_service_request(customer_id: str, issue_type: str, description: str) -> dict:
    return {"sr_number": f"SR{datetime.utcnow():%y%m%d}{uuid4().hex[:4].upper()}", "status": "priority_open"}


def update_address(customer_id: str, new_address: str, otp: str) -> dict:
    return {"updated": otp == "123456", "customer_id": customer_id}


def renew_fd(customer_id: str, fd_id: str, tenure_days: int) -> dict:
    return {"renewed": True, "fd_id": fd_id, "tenure_days": tenure_days}


def block_card(customer_id: str, card_id: str, reason: str) -> dict:
    return {"blocked": True, "card_id": card_id, "replacement_eta": "3 working days"}
