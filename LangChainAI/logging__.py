# from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = DATA_DIR / "support_events.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def configure_logger():
    logger = logging.getLogger("ai_customer_support")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


from datetime import datetime

def log_ticket_event(ticket_id: str, event_type: str, payload: dict[str, Any]) -> str:
    logger = configure_logger()
    entry = {
        "ticket_id": ticket_id,
        "event_type": event_type,
        "payload": payload,
        "timestamp": datetime.now().isoformat() + "Z",
    }
    logger.info(f"Ticket event: ticket id: {ticket_id}, event type: {event_type}")
    return json.dumps(entry, ensure_ascii=False)
