import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db_path() -> Path:
    return Path(__file__).parent / "data" / "outcomes.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_a_id TEXT    NOT NULL,
                persona_b_id TEXT    NOT NULL,
                venue_id     TEXT    NOT NULL,
                outcome      TEXT    NOT NULL
                             CHECK(outcome IN ('went', 'skipped', 'great_date')),
                recorded_at  TEXT    NOT NULL
            )
        """)
        conn.commit()


def record_outcome(
    persona_a_id: str,
    persona_b_id: str,
    venue_id: str,
    outcome: str,
) -> int:
    recorded_at = datetime.now(timezone.utc).isoformat()
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO outcomes
                (persona_a_id, persona_b_id, venue_id, outcome, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (persona_a_id, persona_b_id, venue_id, outcome, recorded_at),
        )
        conn.commit()
        return cursor.lastrowid


def get_outcome_stats() -> dict:
    with _get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) as count FROM outcomes"
        ).fetchone()["count"]

        rows = conn.execute(
            """
            SELECT venue_id, outcome, COUNT(*) as count
            FROM outcomes
            GROUP BY venue_id, outcome
            """
        ).fetchall()

    by_venue: dict = {}
    by_outcome: dict = {"went": 0, "skipped": 0, "great_date": 0}

    for row in rows:
        vid = row["venue_id"]
        out = row["outcome"]
        cnt = row["count"]

        if vid not in by_venue:
            by_venue[vid] = {"went": 0, "skipped": 0, "great_date": 0}
        by_venue[vid][out] = cnt
        by_outcome[out] = by_outcome.get(out, 0) + cnt

    return {
        "total_outcomes": total,
        "by_venue": by_venue,
        "by_outcome": by_outcome,
    }
