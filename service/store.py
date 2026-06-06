"""Lightweight SQLite store for generated decks (history sidebar)."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "decks.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decks (
                id            TEXT PRIMARY KEY,
                title         TEXT NOT NULL,
                tier          INTEGER NOT NULL,
                created_at    TEXT NOT NULL,
                page_count    INTEGER NOT NULL,
                duration_label TEXT NOT NULL,
                model_name    TEXT NOT NULL,
                slug          TEXT,
                payload       TEXT NOT NULL
            )
            """
        )


def save_deck(record: dict) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO decks
            (id, title, tier, created_at, page_count, duration_label, model_name, slug, payload)
            VALUES (:id, :title, :tier, :created_at, :page_count, :duration_label, :model_name, :slug, :payload)
            """,
            {
                "id": record["id"],
                "title": record["title"],
                "tier": record.get("tier", 1),
                "created_at": record["created_at"],
                "page_count": record["page_count"],
                "duration_label": record["duration_label"],
                "model_name": record["model_name"],
                "slug": record.get("slug"),
                "payload": json.dumps(record["payload"], ensure_ascii=False),
            },
        )


def get_deck(deck_id: str) -> Optional[dict]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM decks WHERE id = ?", (deck_id,)).fetchone()
    if not row:
        return None
    return _row_to_summary(row) | {"payload": json.loads(row["payload"])}


def list_grouped() -> list[dict]:
    """Return decks grouped into Today / Yesterday / Earlier (newest first)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, tier, created_at, page_count, duration_label, model_name, slug "
            "FROM decks ORDER BY created_at DESC"
        ).fetchall()

    today = datetime.now(timezone.utc).date()
    groups: dict[str, list[dict]] = {"Today": [], "Yesterday": [], "Earlier": []}
    for row in rows:
        created = _parse_date(row["created_at"])
        delta = (today - created).days if created else 999
        bucket = "Today" if delta <= 0 else "Yesterday" if delta == 1 else "Earlier"
        groups[bucket].append(_row_to_summary(row))

    # Keep only non-empty groups, in display order.
    return [
        {"label": label, "decks": decks}
        for label, decks in groups.items()
        if decks
    ]


def _row_to_summary(row: Any) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "tier": row["tier"],
        "updatedAt": row["created_at"],
        "pageCount": row["page_count"],
        "durationLabel": row["duration_label"],
        "modelName": row["model_name"],
        "slug": row["slug"],
    }


def _parse_date(value: str):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        return None
