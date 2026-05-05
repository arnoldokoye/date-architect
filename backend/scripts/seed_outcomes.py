#!/usr/bin/env python3
"""
Run from the backend/ directory:
    python scripts/seed_outcomes.py

Seeds 8 plausible outcomes into outcomes.db for demo purposes.
Note: not idempotent — running twice inserts duplicates.
Delete backend/app/data/outcomes.db to reset.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import init_db, record_outcome

SEEDS = [
    # (persona_a_id, persona_b_id, venue_id, outcome)
    # Maya + Alex: highly compatible, coffee-forward pair → great date at Elixr
    ("maya",   "alex",   "elixr_coffee",      "great_date"),
    # Jordan + Sam: share Korean culture interest → great date at Manna
    ("jordan", "sam",    "manna_korea",        "great_date"),
    # Jordan + Sam again: second outing, still went
    ("jordan", "sam",    "manna_korea",        "went"),
    # Riley + Alex: mid-energy pair, Phyrst is fine but not special
    ("riley",  "alex",   "the_phyrst",         "went"),
    # Riley + Jordan: algorithm routed to Allen Street — they skipped it
    ("riley",  "jordan", "allen_street_grill", "skipped"),
    # Morgan + Maya: casual pair, Elixr works
    ("morgan", "maya",   "elixr_coffee",       "went"),
    # Sam + Morgan: social pair, Korean BBQ format worked
    ("sam",    "morgan", "manna_korea",        "great_date"),
    # Alex + Riley: opposite routing of Riley+Alex, same skipped pattern
    ("alex",   "riley",  "the_phyrst",         "skipped"),
]

init_db()

for persona_a_id, persona_b_id, venue_id, outcome in SEEDS:
    row_id = record_outcome(persona_a_id, persona_b_id, venue_id, outcome)
    print(f"  [{row_id:02d}] {persona_a_id} + {persona_b_id} @ {venue_id} → {outcome}")

print(f"\n{len(SEEDS)} outcomes seeded. Run python scripts/eval.py to see the distribution.")
