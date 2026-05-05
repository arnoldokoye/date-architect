import sqlite3
from unittest.mock import patch

import pytest

import app.db as db_module
from app.db import get_outcome_stats, init_db, record_outcome


@pytest.fixture
def isolated_db(tmp_path):
    db_file = tmp_path / "test_outcomes.db"
    with patch.object(db_module, "_db_path", return_value=db_file):
        yield db_file


def test_init_db_creates_table(isolated_db):
    init_db()
    conn = sqlite3.connect(str(isolated_db))
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='outcomes'"
    ).fetchall()
    assert len(tables) == 1


def test_init_db_is_idempotent(isolated_db):
    init_db()
    init_db()  # second call must not raise


def test_record_outcome_returns_int(isolated_db):
    init_db()
    row_id = record_outcome("maya", "alex", "elixr_coffee", "great_date")
    assert isinstance(row_id, int)
    assert row_id == 1


def test_record_outcome_increments_id(isolated_db):
    init_db()
    id1 = record_outcome("maya", "alex", "elixr_coffee", "went")
    id2 = record_outcome("jordan", "sam", "manna_korea", "great_date")
    assert id2 == id1 + 1


def test_record_outcome_stores_data(isolated_db):
    init_db()
    record_outcome("maya", "alex", "elixr_coffee", "great_date")
    conn = sqlite3.connect(str(isolated_db))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM outcomes WHERE id=1").fetchone()
    assert row["persona_a_id"] == "maya"
    assert row["persona_b_id"] == "alex"
    assert row["venue_id"] == "elixr_coffee"
    assert row["outcome"] == "great_date"
    assert row["recorded_at"] is not None


def test_get_outcome_stats_empty(isolated_db):
    init_db()
    stats = get_outcome_stats()
    assert stats["total_outcomes"] == 0
    assert stats["by_venue"] == {}
    assert stats["by_outcome"] == {"went": 0, "skipped": 0, "great_date": 0}


def test_get_outcome_stats_aggregates_correctly(isolated_db):
    init_db()
    record_outcome("maya", "alex", "elixr_coffee", "great_date")
    record_outcome("jordan", "sam", "manna_korea", "great_date")
    record_outcome("jordan", "sam", "manna_korea", "went")
    record_outcome("riley", "jordan", "allen_street_grill", "skipped")

    stats = get_outcome_stats()

    assert stats["total_outcomes"] == 4
    assert stats["by_venue"]["elixr_coffee"]["great_date"] == 1
    assert stats["by_venue"]["manna_korea"]["great_date"] == 1
    assert stats["by_venue"]["manna_korea"]["went"] == 1
    assert stats["by_venue"]["allen_street_grill"]["skipped"] == 1
    assert stats["by_outcome"]["great_date"] == 2
    assert stats["by_outcome"]["went"] == 1
    assert stats["by_outcome"]["skipped"] == 1
