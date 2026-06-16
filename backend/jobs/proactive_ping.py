from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from backend.agents.life_event_detector import detect_life_events


def scan_for_life_events() -> list[dict]:
    event = detect_life_events("CUST1001")
    if event and event.confidence > 0.8:
        return [{"customer_id": "CUST1001", "channel": "whatsapp", "message": "Hi Priya, we noticed something that might be relevant to you - want to talk?", "event": event.model_dump()}]
    return []


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_for_life_events, "interval", hours=1, id="life_event_scan", replace_existing=True)
    scheduler.start()
    return scheduler
