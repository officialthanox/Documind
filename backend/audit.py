import json
import os
import uuid
from datetime import datetime
from .config import LOG_FILE


def _load() -> list:
    return json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else []


def _save(history: list):
    json.dump(history, open(LOG_FILE, "w"), indent=2)


def save_entry(question: str, answer: str, chunks: list, confidence: float) -> dict:
    entry = {
        "id": uuid.uuid4().hex[:8],
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "sources_used": sorted({c["source"] for c in chunks}),
        "confidence": confidence,
    }
    history = _load()
    history.append(entry)
    _save(history)
    return entry


def get_all() -> list:
    return _load()


def clear_all():
    _save([])
